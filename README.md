# Music Library Database Web Interface

## Description
This is a PostgreSQL database and a corresponding web interface that can be used to store and access the data within any personal or professional music library. In order to run, you must store your own dataset using the provided SQL schema, and then alter the web schema to use the relevant IP for your system.

![alt text](https://github.com/lankaraniamir/music-library-db-web-interface/blob/master/er_diagram.png?raw=true)
## Database
I created this database to store my own music in a way that made it easy: to extract audio data for my research studies, to find multiple versions of a song for my DJ sets & music production, to listen to my music in traditional forms such as an album, and to allow my library to be shared by my roommates as different users. It contains each entity and relationship that could be found in a typical music streaming service or music archive, along with some more that satisfy the criteria above. The database  is particuarly novel in that there is a distinction between a song and a song file allowing there to be multiple versions of a song that are linked together allowing users to listen to albums as normal while being able to extract alternative versions of the song --- such as instrumentals, acapellas, remixes, and samples --- without hassle.

## Web Interface
Each entity is accessed through unique header options with some headers grouping multiple entities (eg songs, lyrics, & files). Relationships are usually implemented using dynamic links which bring users from the web page for one entity instance to the web page associated with the entity instance of the other entity in the relationship. This constant linkage allows for easy movement between all information as needed (eg can easily go to info of each song on album, each genre of the album, and each user who saved the album from the album page). It also has a dynamic approach to genres where all songs and releases within a genre are found by first finding all subgenres using a recursive selection of all genres that can be traced upwards to the current genre, and then finding any song or release that exists within any of those genres.
Lastly, the web interaface also allows you to create an account and only allows accesss to account holders. 
