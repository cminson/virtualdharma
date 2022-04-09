#!/home/ubuntu/julia-1.6.2/bin/julia
#
# get all new talks via a page crawl.  store result in PATH_NEW_TALKS_WEB
#
  
using Gumbo
using HTTP
using AbstractTrees


URL_CRAWL_TARGET = "https://www.audiodharma.org"
PATH_NEW_TALKS_WEB = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/NEWTALKS_WEB.JSON"



function unpackTR(root)

    #println("\nTR===============")

    htmlTextList = []
    talk_url = "NA"
    series_url = "NA"
    talk = Dict()
    for elem in PreOrderDFS(root) 
        t = typeof(elem)
        if t == HTMLText 
            text = elem.text
            if occursin("Retreat", text) continue end
            if occursin("Detail", text) continue end
            push!(htmlTextList, text)
            #println("HTMLText: $text") 
        end
        if t == HTMLElement{:a}
            #println(elem)
            #println("link")
            data_url = getattr(elem, "data-url", "NA")
            if occursin("mp3", data_url) talk_url = data_url end
            href = getattr(elem, "href", "NA")
            if occursin("series", href) 
                #println("DEV: SERIES SEEN $href")
                series_url = href 
            end
            #println(talk_url)
            #println(href)
        end
    end

    if talk_url != "NA"
        talk["series"] = "NA"
        talk["title"] = htmlTextList[1]
        talk["speaker"] = htmlTextList[2]
        talk["date"]= htmlTextList[3]
        talk["duration"] = htmlTextList[4]
        talk["url"] = talk_url
    else

        series = htmlTextList[1]
        
        talk["series"] = htmlTextList[1]
        talk["title"] = htmlTextList[1]
        talk["speaker"] = htmlTextList[3]
        talk["date"] = htmlTextList[4]
        talk["duration"] = htmlTextList[6]
        talk["url"] = series_url

        println("DEV Setting talk series: $series url: $series_url")
    end

    duration = talk["duration"]
    date = talk["date"]
    println("Duration: $duration")
    if duration == "--" talk = nothing end
    if date == "--" talk = nothing end
    if duration == "00:00" talk = nothing end
    if date == "00:00" talk = nothing end

    println("TALK: $talk")
    return talk

end


function crawlTargetForSeries(url_target, name_of_series)

    # get HTML. generate the HTML element tree
    response = HTTP.get(url_target);
    body = response.body
    html = (String(body))
    doc = parsehtml(html)

    # get first table in this HTML.  that's where we assume talks are stored
    elem_table = [elem for elem in PreOrderDFS(doc.root) if typeof(elem) == HTMLElement{:table}][1]

    # get all the TR elements in this table. one TR per talk (skip the first TR as that's the header)
    listTR = [elem for elem in PreOrderDFS(elem_table) if typeof(elem) == HTMLElement{:tr}][2:end]

    # enumerate all TR elements, pulling in talks for each element
    list_talks = []
    for elem_tr in listTR
        talk = unpackTR(elem_tr)
        if talk == nothing continue end

        talk["series"] = name_of_series
        push!(list_talks, talk)
    end

    return list_talks
end



function crawlTargetForTalks(url_target)

    # get HTML. generate the HTML element tree
    response = HTTP.get(url_target);
    body = response.body
    html = (String(body))
    doc = parsehtml(html)

    # get first table in this HTML.  that's where we assume talks are stored
    elem_table = [elem for elem in PreOrderDFS(doc.root) if typeof(elem) == HTMLElement{:table}][1]

    # get all the TR elements in this table. one TR per talk (skip the first TR as that's the header)
    listTR = [elem for elem in PreOrderDFS(elem_table) if typeof(elem) == HTMLElement{:tr}][2:end]

    # enumerate all TR elements, pulling in talks for each element
    list_talks = []
    for elem_tr in listTR
        talk = unpackTR(elem_tr)
        if talk == nothing continue end

        # if talk is a series, read the Series page it points to and add all the talks
        # otherwise just add the talk
        if talk["url"] == "NA" continue end
        if talk["series"] != "NA"
            url_series = URL_CRAWL_TARGET * talk["url"]
            println("URL $url_series")
            list_series_talks = crawlTargetForSeries(url_series, talk["series"])
            append!(list_talks, list_series_talks)
        else
            push!(list_talks, talk)
        end
    end

    return list_talks
end

function cleanText(text)

    s  = ""
    text = replace(text, "\"" => "")
    text = replace(text, "\\" => "")
    text = replace(text, "\t" => "")
    text = replace(text, "\n" => "")
    text = replace(text, "\r" => "")
    for c in text
        if isprint(c) s *= string(c) end
    end
    return s
end


function storeTalks(new_talks, path_new_talks)

    fd  = open(path_new_talks, "w")

    write(fd, "{\n")
    write(fd,"\t\"talks\":[\n")
    for talk in new_talks

        title = talk["title"]
        url = download_url = talk["url"]
        if length(url) < 1 continue end

        speaker = talk["speaker"]
        

        if occursin("Ying", speaker) speaker = "Ying Chen" end
        if occursin("icon", speaker) continue end

        date = talk["date"]
        duration = talk["duration"]
        series = talk["series"]
        if occursin("NA", series) series = "" end

        
        title = cleanText(title)
        series = cleanText(series)
        if occursin("Guided Meditation", series) series = "Guided Meditations" end
        if occursin("Guided Meditation", title) series = "Guided Meditations" end

        #
        # the download_url is the native url in audiodharma.  
        # that's what we download to local storage
        # the url is the filtered download_url, cleaned up and expressed 
        # just as filename.  that's the name we store
        #
        # get mp3 filename.  prune out escapes and non-ascii characters for our local storage
        download_url_file_name = split(download_url,"/")[end]
        talk_id = split(download_url, "/")[end-1]
        download_url_file_name = replace(download_url_file_name, "%" => "")
        download_url_file_name = replace(download_url_file_name, " " => "")

        download_url = "/" * talk_id * "/" * download_url_file_name
        #print(speaker)

        write(fd, "\t{\n")
        write(fd, "\t\t\"title\":\"" * strip(title) * "\",\n")
        write(fd, "\t\t\"series\":\"" * series * "\",\n")
        write(fd, "\t\t\"url\":\"" * download_url * "\",\n")
        write(fd, "\t\t\"download_url\":\"" * download_url * "\",\n")
        write(fd, "\t\t\"speaker\":\"" * speaker * "\",\n")
        write(fd, "\t\t\"date\":\"" * date * "\",\n")
        write(fd, "\t\t\"duration\":\"" * duration * "\"\n")

        if talk != new_talks[end]
            write(fd, "\t},\n")
        else
            write(fd,"\t}\n")
        end
    end

    write(fd,"\t]\n")
    write(fd,"}\n\n")
    close(fd)

end



#
# Main Entry Point
#
# Gather new talks
# Do some minor cleanup so that badly formed urls don't get into the system
# Validate the talks
# Store result 
#
println("all talks crawler`: start")

NewTalks = []
println("CRAWLING: $URL_CRAWL_TARGET")
new_talks = crawlTargetForTalks(URL_CRAWL_TARGET)
append!(NewTalks, new_talks)

storeTalks(NewTalks,PATH_NEW_TALKS_WEB)



println("complete")


