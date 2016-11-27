#!/usr/local/bin/python
# shows a user's playlists (need to be authenticated via oauth)

import eyed3
import pydub
import sys
import spotipy
import spotipy.util as util

def processTracks(tracks, rippedFile, totalLength, currentStartPosition, playlistName):
    for index, item in enumerate(tracks['items']):
        track = item['track']
        artist = track['artists'][0]['name']
        title = track['name']
        print "Processing: %s %s" % (artist, title)
        endPosition = currentStartPosition + track['duration_ms']
        if endPosition > totalLength:
            endPosition = totalLength

        startM, startS = divmod(currentStartPosition/1000., 60)
        endM, endS = divmod(endPosition/1000., 60)

        if currentStartPosition < totalLength:
            print "Exporting from %d:%d to %d:%d" % (startM, startS, endM, endS)
            currentAudio = rippedFile[currentStartPosition:endPosition]
            currentAudio.export("%s - %s.mp3" % (artist, title), format="mp3")
            currentStartPosition = endPosition
        else:
            print "Ignoring from %d:%d to %d:%d" % (startM, startS, endM, endS)


def writeTags(filePath, artist, title, album):
    audioFile = eyed3.load(filePath)
    if audioFile.tag is None:
        audioFile.initTag()
        audioFile.tag.save()
    audioFile.tag.artist = artist
    audioFile.tag.title = title
    audioFile.tag.album = album
    # audioFile.tag.genre = genre
    #
    # image = open(imagePath,"rb").read()
    # audioFile.tag.images.set(3, image, "image/png", u"cover")

    audioFile.tag.save()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        userName = sys.argv[1]
        playlistName = sys.argv[2]
        rippedFilePath = sys.argv[3]
    else:
        #print "Whoops, need your username!"
        #print "usage: python user_playlists.py [username]"
        sys.exit()

    # Start by getting the ripped file and preparing some data for iterating
    rippedFile = pydub.AudioSegment.from_mp3(rippedFilePath)
    totalLength = len(rippedFile)
    print "Audio file duration is %d:%d" % divmod(totalLength / 1000., 60)
    currentStartPosition = 0

    # Init spotify data, exit if it fails
    token = util.prompt_for_user_token(userName)
    if not token:
        print "Can't get token for", userName
        exit()

    sp = spotipy.Spotify(auth=token)
    playlists = sp.user_playlists(userName)
    for playlist in playlists['items']:
        if (playlist['owner']['id'] == userName and
            playlist['name'] == playlistName):
            results = sp.user_playlist(userName, playlist['id'],fields="tracks, next")
            tracks = results['tracks']
            processTracks(tracks, rippedFile, totalLength, currentStartPosition, playlistName)
            while tracks['next']:
                tracks = sp.next(tracks)
                processTracks(tracks, rippedFile, totalLength, currentStartPosition, playlistName)
