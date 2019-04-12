Database Project by Chinmay Joshi (caj2163) and Ashna Aggarwal (aa4213)

Features implemented - 
PostgreSQL account: aa4213

URL: http://34.73.197.145:8111/

As mentioned in the first part of the project, we implement our own IMDB-like application. We allow users the ability to rate and review movies and TV shows, and also enable them to search for their favoraite media files to look for more details. The details include the language of the media, actors, awards, ratings, reviews and dependeing on the type (movie or series), we have duration or number of episodes and number of seasons. We have also extended the search to look for actors. We display their personal information and list the movies and series they have worked in.

The most interesting page were the search results for media. Depending on the type of media, we had to have conditions about the kind of data we have (runtime or number of episodes and seasons). Also, the ratings were retrieved using this media id and were displayed as their average and count. Another interesting page was the review page where we had to make sure that the user had not reviewed that particular piece of media. So we had to first request the database to get all the reviews and check if the user had revied that media before. Then accordingly, we redirect the user to the appropriate places.

