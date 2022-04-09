#!/home/ubuntu/julia-1.6.2/bin/julia

#
# crawl entire site and store all talks in PATH_ALL_TALKS_WEB
#
# NOTE: this should be used with care!  it will generate some badly formed data that must be cleaned up.
# Use with caution.
#
  
using Gumbo
using HTTP
using AbstractTrees


URL_CRAWL_TARGET = "https://www.audiodharma.org"
MAX_AD_PAGES = 1
MAX_AD_PAGES = 358

PATH_ALL_TALKS_WEB = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/TEST.JSON"
PATH_TALKS_TOP = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/TOP200.JSON"
PATH_TALKS_TRENDING = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/TOP2DAYS.JSON"
PATH_TALKS_TOP3MONTHS = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/TOP90DAYS.JSON"


CharExclusions = ["\"", "/", "\t", "\n", "\r"]


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
        date = talk["date"]
        duration = talk["duration"]
        series = talk["series"]

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

        url_file_name = split(url,"/")[end]
        url_file_name = replace(url_file_name, "%" => "")
        url_file_name = replace(url_file_name, " " => "")
        #url_file_name = "".join([i if ord(i) < 128 else '' for i in url_file_name])

        url = url_file_name
        download_url = "/" * talk_id * "/" * download_url_file_name
        #print(speaker)
        series = replace(series, "NA" => "")

        write(fd, "\t{\n")
        write(fd, "\t\t\"title\":\"" * strip(title) * "\",\n")
        write(fd, "\t\t\"series\":\"" * series * "\",\n")
        write(fd, "\t\t\"url\":\"" * download_url * "\",\n")
        #write(fd, "\t\t\"download_url\":\"" * download_url * "\",\n")
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
# Gather all talks
#
# Validate the talks
# Store result 
#
println("all talks crawler`: start")

AllTalks = []
for i in 1:MAX_AD_PAGES
#for i in 275:275
#for i in 69:69

    url_target = URL_CRAWL_TARGET * "?page=" * string(i)
    println("CRAWLING: $url_target")
    new_talks = crawlTargetForTalks(url_target)
    append!(AllTalks, new_talks)
    #sleep(5)
end

DupDict = Dict()
AllUniqueTalks = []
for talk in AllTalks

    #println(talk)
    url = talk["url"]
    file_name = split(url,"/")[end]
    if haskey(DupDict, file_name) 
        series_old = DupDict[file_name]["series"]
        series_new = talk["series"]
        println("DUP!!!!")
        continue
    end

    println("Setting Unique")
    DupDict[file_name] = talk
    push!(AllUniqueTalks, talk)

end


storeTalks(AllUniqueTalks,PATH_ALL_TALKS_WEB)




println("complete")


