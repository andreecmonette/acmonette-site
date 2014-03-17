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

One of the core concerns we had when writing DistroWeb is that we wanted to reduce our reliance on centralized servers as much as possible. We took our inspiration from distributed protocols (most notably [BitTorrent](http://en.wikipedia.org/wiki/BitTorrent)). Traditionally, BitTorrent files have been accessed through central tracker files, but more recently people have been using the Kademlia protocol to find files on a network. DistroWeb reimplements the distributed hash table idea that is at the heart of protocols like Kademlia. Currently, this is implemented by providing (currently, hardcoding) a list of some peers which is distributed to each node on initial startup. When a page is requested via a hash, the [Hamming distance](http://en.wikipedia.org/wiki/Hamming_distance) between the binary encodings of the hash and each peer's node ID is calculated, and then a request for the hash including the port being listened on is passed along to the "closest" peer to that node. If the connection fails, the request is passed to the next closest and so on. At the receiving end, the node pushes the address that the connection was received on and the port it is listening on onto the request and continues to relay it until it reaches a node that doesn't have any closer nodes listed. This peer then "takes responsibility" for the file, serving whatever tracker information it has on that hash to the originator, and accepting notifications from nodes that a particular version of a file is being served. 

## Peer regeneration

[^1]If a peer times out or does not respond to DistroWeb requests while searching for a file, other peers are asked for some of their peers in order to replace the missing peers. Peers that initiate a DistroWeb request are also added to the recipient's peers list, up to a limit. Peers that time out are only removed from a list if they can be replaced - if the end of the peers list is reached without making a valid connection the assumption is made that the client's network connection is temporarily nonfunctional. When peers are replaced or added, the list of tracker files will be checked to see whether any new peers are closer to some of the node's tracked hashes than the node themselves, and if they are, those tracker files will be sent to the nodes in question for concatenation to whatever tracker file they have currently. 

## Signed versioning

(As of March 17, this hasn't been implemented yet either.) Documents will carry a header signed with the private key corresponding to their hash - this signature will consist of a version number and checksum of the content. Additionally, the tracker packets will keep track of version numbers, to more easily facilitate updating of content. If a tracker node is informed that someone is seeding a newer version of a document, it will check that the document corresponds to the same hash and then notify the nodes that it is tracking that a newer version is available. (Generally, this will happen first when the owner of the document updates it and sends a notification about updating it into the DHT). 

## Client-based naming

Clients can choose the names that they apply to documents, but documents include a suggested name that the client will associated with a given hash.

[^1]: (As of March 17, this hasn't been implemented yet.) 
