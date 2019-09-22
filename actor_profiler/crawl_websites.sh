#! /bin/bash

basedir="`pwd`/crawled_dataset"
ts=`date +"%Y-%m-%d_%H-%M-%S"`

crawl_website() {
  # $1: url
  # $2: website name
  mkdir -p "$basedir/$2"
  wget $1 -O "$basedir/$2/$2-$ts.html" 2>>"$basedir/$2/error.log"
}


crawl_website "https://www.foxnews.com/" "Fox_News"
crawl_website "https://chromereleases.googleblog.com/" "Chrome_Release_Blog"
crawl_website "https://kimbellart.org/events" "Kimbell_Art_Museum"
crawl_website "https://earthquaketrack.com/r/east-coast-of-honshu-japan/recent" "Earthquake_Track_in_Japan"
crawl_website "https://weather.com/weather/tenday/l/New+York+NY+10010:4:US" "Weather_in_New_York"

crawl_website "https://www.yahoo.com/news/" "Yahoo_News"
crawl_website "https://www.usatoday.com/" "USA_Today"
crawl_website "https://www.nytimes.com/" "The_NY_Times"
crawl_website "https://www.starwars.com/news" "StarWars_official"
crawl_website "http://www.espn.com/nba/schedule" "ESPN_NBA"
crawl_website "https://www.reddit.com/r/nba" "Reddit_NBA"
crawl_website "https://mobile.twitter.com/HoustonRockets" "Twitter_Houston_Rockets"
crawl_website "https://mobile.twitter.com/SouthPark" "Twitter_South_Park"
crawl_website "https://www.brooklynmuseum.org/calendar" "Brooklyn_Museum"
crawl_website "https://cincinnatiartmuseum.org/events-programs/events-list/" "Cincinnati_Art_Museum"
crawl_website "https://www.trinitychurchboston.org/calendar" "Trinity_Church_Boston"
crawl_website "http://www.oraclearena.com/events" "Oracle_Arena"
crawl_website "https://www.ebay.com/urw/Apple-Lightning-to-USB-Cable-1m-White-MD818ZM-A-/product-reviews/134466773?_itm=191482438168&sort=-lastEditedDate" "Ebay"
crawl_website "https://www.boston.gov/events" "Boston_gov"
crawl_website "https://www.ted.com/tedx/events" "TEDx_events"
crawl_website "https://air.plumelabs.com/en/live/beijing" "World_Air_Map_Beijing"
crawl_website "https://air.plumelabs.com/en/week/new-york" "World_Air_Map_New_York"
crawl_website "https://www.timeanddate.com/moon/phases/usa/new-york" "Moon_phase_New_York"
crawl_website "https://www.usharbors.com/harbor/new-york/new-york-the-battery-ny/tides/#harbor-nav" "Tides_New_York"
crawl_website "https://coinmarketcap.com/currencies/volume/24-hour/" "Crypto_day_transction_volume"
crawl_website "https://earthobservatory.nasa.gov/topic/image-of-the-day" "NASA_IOTD"
crawl_website "https://www.isitdownrightnow.com/" "IsItDown"

