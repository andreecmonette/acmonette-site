Title: DistroWeb: past, present, and future
Date: 2014-03-16 23:30
Category: Programming
Tags: hacker school, coding, distroweb
Slug: distroweb
Author: Andree Monette
Summary: Distroweb

The idea for [DistroWeb](https://github.com/sudowhoami/distroweb/) came to [Rose Ames](https://github.com/sudowhoami/) and I during a [late-night Japanese curry dinner](http://www.gogocurryusa-ny.com/) after having just seen [Richard Stallman's talk at the Cooper Union](http://www.meetup.com/ny-tech/events/164513032/) on free software. We didn't implement any ideas from the talk itself, but it got us in a mood of thinking about distributed systems. We chatted about what major centralized systems could be decentralized. A few major examples came to mind:

* Website hosting. Frequently, content is hosted on a single server or set of servers and served from that centralized location to clients who ask for it. When content is mirrored, a central location points to mirrors, which is quite easy to target or disrupt.
* The [domain name](http://en.wikipedia.org/wiki/Domain_Name_System) system - essentially, it's controlled by a small committee of developers from seven different countries, who all meet in data centres in the US a few times a year to renew the keys for the root DNS server.
* Search is also centralized, mostly around such companies as Google.

DistroWeb is essentially an [overlay network](http://en.wikipedia.org/wiki/Overlay_network) over the Internet that imitates the World Wide Web, serving documents to browsers from remote machines that are uniquely identified by a URL - currently, that URL is `http://localhost:1234/distroweb/<hash>`, with `<hash>` serving as a unique identifier for each page. Right now, a lot of the functionality is hardcoded, but we're looking to fix that later in the Hacker School batch. Installation requires [node.js](http://nodejs.org/), and is quite simple:

    > git clone git://github.com/sudowhoami/distroweb/
    > cd distroweb
    > node distroweb.js
    Welcome to distroWeb!  Spinning up servers...
    Proxy:  Listening on port 1234
    Server:  Listening on port 12345
    DHT:  Listening on port 54321
    All servers started ok

This can be followed by browsing to pages encoded in the above format.[^2] 

Once the server is running, users can browse DistroWeb by visiting pages encoded in the above format. (At the time of initial writing, we haven't implemented a lot of features like bootstrapping a person's initial list of peers, or implementing [TCP hole punching](http://en.wikipedia.org/wiki/TCP_hole_punching), so fetching documents might require a bit of code-diving — however, I'm documenting here what we have left to write and will add addenda as these features are coded and DistroWeb gets closer to "release".)

# The design of DistroWeb

The following is a combination of documentation and design spec, with the intention of shifting the points here from the latter into the former category as the remaining DistroWeb functionality gets coded, probably in early April.

## High-level design

A DistroWeb node is initialized by executing the file `distroweb.js`, which serves as a wrapper file that starts three servers - distroProxy, which receives HTTP GET requests from the browser, distroServer, which handles content delivery (in conjunction with distroClient) between nodes based on requests using the distroWeb protocol, and the DHT, a distributed hash table which is used to look up metadata about a requested hash (including, crucially, which nodes are "seeding" that hash, so that the distroClient can issue requests to that node).

## Distributed hash table

One of the core concerns we had when writing DistroWeb is that we wanted to reduce our reliance on centralized servers as much as possible. We took our inspiration from distributed protocols (most notably [BitTorrent](http://en.wikipedia.org/wiki/BitTorrent)). Traditionally, files shared through BitTorrent have been accessed through central tracker files, but more recently people have been using the Kademlia protocol to find files on a network. DistroWeb reimplements the distributed hash table idea that is at the heart of protocols like Kademlia. Currently, this is implemented by providing (currently, hardcoding) a list of some peers which is distributed to each node on initial startup. When a page is requested via a hash, the [Hamming distance](http://en.wikipedia.org/wiki/Hamming_distance) between the binary encodings of the hash and each peer's node ID is calculated, and then a request for the hash including the port being listened on is passed along to the "closest" peer to that node. If the connection fails, the request is passed to the next closest and so on. At the receiving end, the node pushes the address that the connection was received on and the port it is listening on onto the request and continues to relay it until it reaches a node that doesn't have any closer nodes listed. This peer then "takes responsibility" for tracking the document, serving whatever tracker information it has on that hash to the originator, and accepting notifications from nodes that a particular version of a file is being served. If it doesn't currently track that file, it creates a tracker file and sends the empty string as a response. Abstractly, the distributed hash table is implemented as an interface for creating and adding metadata about a file, with the tracker node handling cleanup of dropped nodes and obsolete data. A final feature to increase redundancy and scalability for popular files involves having nodes that route many requests for a tracker file take responsibility for tracking it themselves. This should allow the network to be robust against trackers failing, as tracker files will get distributed to other accessible nodes near that file. 

## Peer regeneration

[^3]If a peer times out or does not respond to DistroWeb requests while searching for a file, other peers are asked for some of their peers in order to replace the missing peers. Peers that initiate a DistroWeb request are also added to the recipient's peers list, up to a limit. Peers that time out are only removed from a list if they can be replaced - if the end of the peers list is reached without making a valid connection the assumption is made that the client's network connection is temporarily nonfunctional. When peers are replaced or added, the list of tracker files will be checked to see whether any new peers are closer to the node's tracked hashes than the node itself, and if they are, those tracker files will be sent to the nodes in question for concatenation to whatever tracker file they currently have. 

## Signed versioning

[^4]Documents will carry a header signed with the private key corresponding to their hash - this signature will consist of a version number and checksum of the content. Additionally, the tracker packets will keep track of version numbers, to more easily facilitate updating of content. If a tracker node is informed that someone is seeding a newer version of a document, it will check that the document corresponds to the same hash and then notify the nodes that it is tracking that a newer version is available. (Generally, this will happen first when the owner of the document updates it and sends a notification about updating it into the DHT). Thus, someone who hosts a page on the DistroWeb can update their page simply by generating a new signature with a higher version number and requesting it, at which point it will be seeded by listening nodes tracked by the tracker.

## Client-based naming

[^5]Clients can choose the names that they apply to documents, but documents include a suggested shortname and longname that the client will associated with a given hash. For example, if a page uses `bob` as a shortname, and `bobs_cutlery` as a longname, a user that has accessed that hash once will be able to browse to it at `http://localhost:1234/distroweb/bob`, `http://localhost:1234/distroweb/bobs_cutlery`, or the original hash. Name collisions will be handled by defaulting to the long name or appending a numeral to the name. Initial linking will be done by hash, but once a page is accessed the proxy server will issue a 301 redirect to the actual page. Pages on the World Wide Web can also be referenced and linked to within DistroWeb pages; `http://localhost:1234/www.reddit.com` returns a 301 to `http://www.reddit.com/`, for example.

## Distributed vote-based search

[^6]Searching DistroWeb involves sending out UDP packets with the search query to all of one's neighbors, who then pass along the packet, sending votes for a particular page back. If a node is storing a page and wishes to index it for public search, they do so by using their node ID to create a unique mapping from words to bitmasks, then use these bitmasks in constructing a [Bloom filter](http://en.wikipedia.org/wiki/Bloom_filter) for that document. These Bloom filters, along with the hashes used to create them, are passed along to trackers for that document (through the DHT), which run checks against incoming search queries and send back the IDs of matched hashes. The matched hashes are then compiled together at the client end into a list, ranked by the number of matched Bloom filters. 

[^1]: We may end up having the installation attempt to alias distroweb to localhost, to produce http://distroweb/ urls.

[^2]: At the time of initial writing, we haven't implemented a lot of features like bootstrapping a person's initial list of peers, or implementing [TCP hole punching](http://en.wikipedia.org/wiki/TCP_hole_punching), so fetching documents might require a bit of code-diving - however, I'm documenting here what we have left to write and will add addenda as these features are coded and DistroWeb gets closer to "release".

[^3]: As of March 17, this hasn't been implemented yet - only the proxy, file fetcher, and DHT have been implemented - but the plan is to implement it in April. These footnotes will be amended as these features are added.

[^4]: This also hasn't been implemented.

[^5]: This isn't implemented yet either, except for the external redirect to the web.

[^6]: Also not yet implemented.
