## Notes:

### Meaning / logistics
- Since a street can have many frequencies - when a vehicle passes the street, does it skip those bins with higher frequency, which it doesn't really need to pick up
- like is it more efficient to ***pick up half-full bins*** or ***make multiple passes***
-  guess it decides on each pass wrt frequency / deadline until going below frequency

### Technical stuff
- all graph files have - NumberOfFractions:	1
- edge number - dense_rank of edge id
- edge_id - id of edge in larger graph I guess
- in first graph file after line 1120 (edge number 1111), edge id is -1, and every next one is previous-1, decreasing
