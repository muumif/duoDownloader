import requests
import re
import ffmpeg
import multiprocessing

epCount = 0 # Number of episodes
seasons = [] # Number of episodes in each season
baseUrl = "" # Base URL of the series

def get_m3u8_url(url: str):
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            m3u8_urls = re.findall(r'(https?://\S+\.m3u8)', response.text)
            
            if m3u8_urls:
                return m3u8_urls[0]
            else:
                return "No m3u8 stream URL found"
        else:
            return f"HTTP request failed with status code {response.status_code}"
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
def startFfmpeg(url: str, ep: int, cpuEncoding: bool):
      season = getSeason(ep)
      if cpuEncoding:
            stream = ffmpeg.input(url)
            stream = ffmpeg.output(stream, f"out/YhikarotidS{season}E{ep}.mkv", vcodec="libx265", loglevel="error")
            ffmpeg.run(stream)
      else:
            stream = ffmpeg.input(url)
            stream = ffmpeg.output(stream, f"out/YhikarotidS{season}E{ep}.mkv", vcodec="hevc_nvenc", loglevel="error")
            ffmpeg.run(stream)

def getSeason(ep: int):
      season = 1
      for i in range(len(seasons)):
            if ep <= seasons[i]:
                  season = i + 1
                  break
            ep -= seasons[i]
      return season

if __name__ == "__main__":
      maxWorkers = 10
      numIter = (epCount - 1) // maxWorkers + 1
      for i in range(numIter):
            startEp = i * maxWorkers + 1
            endEp = min((i + 1) * maxWorkers, epCount)
            proccesses = []
            print(f"Starting from {startEp} to {endEp}")
            for j in range(startEp, endEp + 1):
                  url = f"{baseUrl}?ep={j}"
                  m3u8_url = get_m3u8_url(url)
                  p = multiprocessing.Process(target=startFfmpeg, args=(m3u8_url, j, j % 2 == 0))
                  proccesses.append(p)
                  p.start()
            
            for p in proccesses:
                  p.join()
            print(f"Finished from {startEp} to {endEp}")
      print("All done!")