Title: DistroWeb: past, present, and future
Date: 2014-03-16 23:30
Category: Programming
Tags: hacker school, coding, distroweb
Slug: distroweb
Author: Andree Monette
Summary: Distroweb

The idea for [DistroWeb](https://github.com/sudowhoami/distroweb/) came to [Rose Ames](https://github.com/sudowhoami/) and I during a [late-night Japanese curry dinner](http://www.gogocurryusa-ny.com/) after having just seen [Richard Stallman's talk at the Cooper Union](http://www.meetup.com/ny-tech/events/164513032/) on free software. We didn't really implement any ideas in particular from the talk itself, which I felt had a number of pretty difficult pills for people to swallow, such as ceasing use of mobile phones and the like. However, the talk got us in a mood of thinking about decentralized networks and distributed systems, so we got to chatting about what major systems could be decentralized but aren't. A few major examples came to mind:

* One of the biggest ones was hosting. Frequently, content is hosted on a single server or set of servers and served from that centralized location to clients who ask for it. When content is mirrored, the mirrors are often pointed to from a central location which is quite easy to target or disrupt.
* Another system that is highly centralized is the [domain name](http://en.wikipedia.org/wiki/Domain_Name_System) system - essentially, it's controlled by a small committee of developers from seven different countries, who all meet in data centres in the US a few times a year to renew the keys for the root DNS server.
* Search is also centralized, mostly around such companies as Google.

DistroWeb is essentially an [overlay network](http://en.wikipedia.org/wiki/Overlay_network) over the Internet that imitates the World Wide Web, serving documents to browsers from remote machines that are uniquely identified by a URL - currently, that URL is `http://localhost:1234/distroweb/<hash>`, with `<hash>` serving as a unique identifier for each page. Right now, a lot of the functionality is hardcoded, but we're looking to fix that later in the Hacker School batch. Usage is quite simple, and requires [node.js](http://nodejs.org/), which DistroWeb was coded for: 

    > git clone git://github.com/sudowhoami/distroweb/
    > cd distroweb
    > node distroweb.js
    Welcome to distroWeb!  Spinning up servers...
    Proxy:  Listening on port 1234
    Server:  Listening on port 12345
    DHT:  Listening on port 54321
    All servers started ok

This can be followed by browsing to pages encoded in the above format. (At the time of initial writing, we haven't implemented a lot of features like bootstrapping a person's initial list of peers, or implementing [TCP hole punching](http://en.wikipedia.org/wiki/TCP_hole_punching), so fetching documents might require a bit of code-diving - however, I'm documenting here what we have left to write and will add addenda as these features are coded and DistroWeb gets closer to "release".)

# How DistroWeb works, present and future

The following is a combination of documentation and design spec, with the intention of shifting the points here from the latter into the former category as the remaining DistroWeb functionality gets coded, probably in early April.

## High-level design

A DistroWeb node is initialized by executing the file distroweb.js, which serves as a wrapper file that starts three servers - distroProxy, which receives http GET requests from the browser, distroServer, which handles content delivery (in conjunction with distroClient) between nodes based on requests using the distroWeb protocol, and the DHT, a distributed hash table which is used to look up metadata about a requested hash (including, crucially, which nodes are "seeding" that hash, so that the distroClient can issue requests to that node).

## Distributed hash table

One of the core concerns we had when writing DistroWeb is that we wanted to reduce our reliance on centralized servers as much as possible. We took our inspiration from distributed protocols (most notably [BitTorrent](http://en.wikipedia.org/wiki/BitTorrent)). 
