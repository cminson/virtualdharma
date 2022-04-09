#!/usr/bin/env python

# MP3 Wrapper for Signal_Power (which operates on wave files)
# Provide functions for normalizing the speech power of an MP3 recording to a fixed dB value
# and for trimming dead air from the beginning and ending of the recording.

# A command line utility is provided at the bottom that uses this class.

import os
import sys
import shutil
import tempfile
import wave

from Signal_Power import Signal_Power, Endpointer
import mutagen
from mutagen.mp3 import MP3

class Optionset:
    def __init__(self):
        self.quiet = False
        self.dryrun = False
        self.no_power = self.no_trim = self.no_resample = False
        self.dopower = self.dotrim = self.doresample = True
        self.save_scraps = False
        self.verbose = False
        self.standard_db = -20.0
        self.maximum_allowed_average_power_in_db = -10.0
        self.margin_db = 3.0
        self.scrapdir = None
        self.plotdir = None
        self.plot = False
        self.backupdir = None

Options = Optionset()

OptionsTable = [
    ('verbose', 'v', "Print processing steps"),
    ('quiet', 'q', "Only print errors"),
    ('no-power', 'N', "Don't normalize power level"),
    ('no-trim', 'T', "Don't trim silence from beginning and end"),
    ('no-resample', 'R', "Don't resample to 44.1kHz (normally done if not already 44100)"),
    ('dryrun','n', "Don't modify file, just show what would be done (equivalent to -N -T -R)"),
    ('save-scraps', 'S', "Save silence from beginning and end in <file>_prefix.mp3 and <file>_suffix.mp3 files"),
    ('standard-db=', 'd', "Value to normalize speech power to (default -30dB)"),
    ('margin-db=', 'm', "DB tolerance margin below which no normalization is performed (default 3dB)"),
    ('plotdir=', None, "directory where plots should be placed"),
    ('scrapdir=', None, "directory where trimming scraps should be placed"),
    ('plot', 'p', "Plot silence and speech power distribution to <file>_power.png"),
]


def system(cmd):
    if Options.verbose:
        print cmd
    os.system(cmd)

def maketemp(ext='.wav'):
    fd, name = tempfile.mkstemp(ext)
    os.fdopen(fd).close()
    return name

class Mp3RecordingNormalizer:
    def __init__(self, inputfile, debugging=False):
        if Options.backupdir:
            shutil.copy(inputfile, Options.backupdir)

        self.filename, self.ext = os.path.splitext(inputfile)
        self.ext = self.ext.lower()
        if self.ext == '.mp3':
            self.mp3file = inputfile
            self.wavfile = None
            wavefile = self.get_persisted_wavefile_name()
            if os.path.exists(wavefile) and os.stat(wavefile).st_mtime >= os.stat(inputfile).st_mtime:
                self.wavfile = wavefile
        elif self.ext == '.wav':
            self.mp3file = None
            self.wavfile = inputfile
        else:
            raise Exception("Inputfile (%s) must be .mp3 or .wav file" % inputfile)
        
        self.power = None
        self.plotdir = None
        self.get_info()

        self.dirty = False
        self.ignore_output = '' if debugging else '>%s 2>&1' % os.devnull

    def convert_to_wave(self):
        if not self.wavfile:
            self.wavfile = maketemp()
            system('mp3sDecoder -if "%s" -of "%s" %s ' % (self.mp3file, self.wavfile, self.ignore_output))

    def get_persisted_wavefile_name(self):
        return os.path.splitext(self.mp3file)[0] + '.wav'
    
    def set_plotdir(self, plotdir):
        self.plotdir = plotdir

    def save_wave(self):
        if self.mp3file:
            self.convert_to_wave()
            wavefile = self.get_persisted_wavefile_name()
            if not os.path.exists(wavefile):
                shutil.move(self.wavfile, wavefile)
                self.wavfile = wavefile
        
    def get_info(self):
        if self.ext == '.mp3':
            mp3 = mutagen.File(self.mp3file, [MP3])
            info = mp3.info
            self.mode = 'mono' if info.mode == 3 else 'stereo'
            self.sampling_rate = info.sample_rate
            self.bit_rate = info.bitrate
            self.duration_in_seconds = info.length
        else:
            wav = wave.open(self.wavfile)
            self.mode = 'mono' if wav.getnchannels() == 1 else 'stereo'
            self.sampling_rate = wav.getframerate()
            self.bit_rate = self.sampling_rate * wav.getnchannels() * 16
            self.duration_in_seconds = wav.getnframes() / float(self.sampling_rate)
            

    def is_resampling_needed(self):
        return self.sampling_rate != 44100
        
    def ensure_44100(self):
        if self.is_resampling_needed():
            self.convert_to_wave()
            outfile = maketemp()
            system('sox "%s" -r 44100 "%s"' % (self.wavfile, outfile))
            os.unlink(self.wavfile)
            self.dirty = True
            self.wavfile = outfile
            self.sampling_rate = 44100
            return True

    def save(self):
        if self.dirty:
            if self.ext == '.mp3':
                # Set a floor of 64kbps because below this the mp3sEncoder
                # will produce an mp3 that's at 22.05kHz.
                if self.mode == 'mono':
                    bit_rate = max(64000, self.bit_rate) 
                    system('mp3sEncoder -q 1 -br %s -if "%s" -of "%s" %s' % \
                       (bit_rate, self.wavfile, self.mp3file, self.ignore_output))
                # IMC Change. if stereo, downconvert to mono to make sure intros work
                else:
                    bit_rate = max(64000, self.bit_rate) 
                    system('mp3sEncoder -q 1 -br %s -if "%s" -of "%s" %s -mono' % \
                       (bit_rate, self.wavfile, self.mp3file, self.ignore_output))
            self.dirty = False

    def analyze_power(self):
        if not self.power:
            self.convert_to_wave()
            self.power = Signal_Power(self.wavfile)
            self.power.compute()
                
    def plot(self, suffix=''):
        self.analyze_power()
        title=os.path.split(self.filename)[1]
        plotfile = self.filename+'_'+suffix + '.png'
        if self.plotdir:
            plotfile = os.path.join(self.plotdir, os.path.basename(plotfile))
        return self.power.plot(title, plotfile)
        
    def get_trim_points(self):
        self.analyze_power()
        ep = Endpointer()
        ep.load_signal_power(self.power)
        start = ep.get_start_of_speech()
        end = ep.get_end_of_speech()
        speech_portion = ep.get_speech_portion()
        return (start, end, speech_portion)
    
    def power_adjustment_factor(self, final_db, tolerance_db):
        self.analyze_power()
        signal_db = max(self.power.speech_db, self.power.average_db)
#        signal_db = self.power.speech_db if self.power.snr >= 20 else self.power.average_db
        adjustment = final_db - signal_db
        # don't let normalizer push average power above Options.maximum_allowed_average_power_in_db in any case
#        if (self.power.average_db + adjustment) > Options.maximum_allowed_average_power_in_db:
#            adjustment = Options.maximum_allowed_average_power_in_db - self.power.average_db
        return (abs(adjustment) > tolerance_db), adjustment
        
    def normalize_power(self, final_db=-30, tolerance_db=3):
        self.analyze_power()
        adjustment_needed, adjustment_amount = self.power_adjustment_factor(final_db, tolerance_db)
        if adjustment_needed:
            scalefactor = 10**(adjustment_amount/20.0)
            outfile = maketemp()
            system("sox -v %f %s %s %s" % \
                   (scalefactor, self.wavfile, outfile, self.ignore_output))

            self.power = None # invalidate power statistics
            os.unlink(self.wavfile)
            self.wavfile = outfile
            self.dirty = True
        return adjustment_needed

    def close(self):
        self.save()
        if self.wavfile and self.ext == '.mp3':
            os.unlink(self.wavfile)
            self.wavfile = None

def mp3cut(filename, start, end, savescraps = False, scrapdir = None):
    from pymp3cut import MP3File
    filebase=os.path.splitext(filename)[0]
    scrapbase = filebase
    if scrapdir:
        scrapbase = os.path.join(scrapdir, os.path.basename(filebase))

    # cut and save prefix
    if start and savescraps:
        file = MP3File(filename)
        file.calculate_segment('%s,%s,%s' % (scrapbase + '_prefix.mp3', 0, start))
        file.cut_segment()

    # cut and save endpointed center (the payload)
    payload = None
    if start or end:
        file = MP3File(filename)
        payload = filebase + '_payload.mp3'
        segment = '%s,%s' % (payload, start or 0)
        if end:
            segment += ',%s' % end
        file.calculate_segment(segment)
        file.cut_segment()

    # cut and save suffix
    if end and savescraps:
        file = MP3File(filename)
        file.calculate_segment('%s,%s' % (scrapbase + '_suffix.mp3', end))
        file.cut_segment()

    if payload:
        shutil.move(payload, filename)
            

def usage(options):
    print '''usage: PublishMp3SpeechFile [options] <file.mp3> [<file1.mp3> [...]]

Prepare an MP3 speech recording for publication by:
    1) Normalizing volume to -30dB
    2) Trimming dead air from beginning and end
    '''
    for i in options:
        print i
    sys.exit(1)
        

from distutils.fancy_getopt import FancyGetopt
def main():
    F = FancyGetopt(OptionsTable)
    args = F.getopt(object=Options)
    if len(args) < 1:
        usage(F.generate_help())

    Options.dopower = not Options.no_power
    Options.dotrim = not Options.no_trim
    Options.doresample = not Options.no_resample
    if Options.dryrun:
        Options.dopower = Options.dotrim = Options.doresample = False
        
    for filename in args:

        results = process(filename)

        if not Options.quiet:
            print 'Volume Adjustment: %+.0fdB  (Speech %.0fdB, Background %.0fdB, Average %.0fdB, SNR %.0fdB)' % \
                  (results.power_adjustment, results.speech_db, results.background_db, results.average_db, results.snr)

            if results.trim_needed:
                print 'Trim from start: %d seconds, from end: %d seconds' % (results.trim_start, results.trim_end)

            if results.resampling_needed:
                print 'Sampling rate is %skHz and will be converted to 44100kHz' % results.sampling_rate

class Results:
    def __init__(self):
        self.normalization_needed = False
        self.power_adjustment = 0.0

        self.trim_needed = False
        self.trim_failed = False
        self.trim_start = 0
        self.trim_end = 0

        self.mp3_bitrate = 0
        self.resampling_needed = False
        self.sampling_rate = 0
        self.speech_db = self.background_db = self.average_db = self.snr = 0.0
        self.speech_portion = 0.0
        self.compute_failure = None
        
        self.before_plot = self.after_plot = None

    def summary(self):
        notes = ''
        if self.normalization_needed:
            notes += 'The recording volume was adjusted '
            notes += 'up' if self.power_adjustment > 0 else 'down'
            notes += ' by %+ddB. ' % self.power_adjustment
        else:
            notes += "The recording's volume level was just right. "
            
        notes += '(Originally Speech was %.0fdB, Background was %.0fdB, Average was %.0fdB, SNR %.0fdB) ' % \
                 (self.speech_db, self.background_db, self.average_db, self.snr)

        if self.trim_needed:
            notes += 'Trimmed %d seconds from start, %d seconds from end. ' % (self.trim_start, self.trim_end)

        if self.resampling_needed:
            notes += 'Sampling rate was %skHz and has been converted to 44100kHz' % self.sampling_rate

        if not notes:
            notes = 'No work was performed'

        return notes
        
        
# Process one file, according to Options.
# Return results

def process(filename):
    results = Results()

    mp3norm = Mp3RecordingNormalizer(filename, debugging=Options.verbose)

    mp3norm.set_plotdir(Options.plotdir)
    
    mp3norm.analyze_power()
    if mp3norm.power.compute_failure:
        results.compute_failure = 'Compute failure: ' + mp3norm.power.compute_failure
        return results

    results.normalization_needed, results.power_adjustment = \
               mp3norm.power_adjustment_factor(Options.standard_db, Options.margin_db)

    results.speech_db = mp3norm.power.speech_db
    results.background_db = mp3norm.power.background_db
    results.average_db = mp3norm.power.average_db
    results.snr = mp3norm.power.snr
    results.bit_rate = mp3norm.bit_rate

    if Options.plot:
        results.before_plot = mp3norm.plot('before')
        
    if mp3norm.power.snr < 20:
        results.trim_failed = True
    else:
        start_crop, end_crop, speech_portion = mp3norm.get_trim_points()
        results.trim_needed = (start_crop != None) or (end_crop != None)
        results.trim_start = start_crop or 0
        results.trim_end = trimend = mp3norm.duration_in_seconds - (end_crop or mp3norm.duration_in_seconds)
        results.speech_portion = speech_portion
        results.duration_in_minutes = mp3norm.duration_in_seconds/60.0
                
    results.sampling_rate = mp3norm.sampling_rate
    results.resampling_needed = mp3norm.is_resampling_needed()

    if Options.dopower:
        mp3norm.normalize_power(Options.standard_db, Options.margin_db)

    if Options.doresample:
        mp3norm.ensure_44100()

    if Options.plot:
        results.after_plot = mp3norm.plot('after')
        
    mp3norm.save() # convert wave back to mp3 for trim step
                
    if Options.dotrim and results.trim_needed:
        try:
            mp3cut(filename, start_crop, end_crop, Options.save_scraps, Options.scrapdir)
        except:
            print 'Trouble trimming file -- left untrimmed'

    os.chmod(filename, 0666)
    mp3norm.close()

    return results

if __name__ == '__main__':
    main()
    

