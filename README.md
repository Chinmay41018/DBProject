Database Project by Chinmay Joshi (caj2163) and Ashna Aggarwal (aa4213)

Features implemented - 
PostgreSQL account: aa4213

URL: http://35.190.167.214:8111/

As mentioned in the first part of the project, we implement our own IMDB-like application. We allow users the ability to rate and review movies and TV shows, and also enable them to search for their favoraite media files to look for more details. The details include the language of the media, actors, awards, ratings, reviews and dependeing on the type (movie or series), we have duration or number of episodes and number of seasons. We have also extended the search to look for actors. We display their personal information and list the movies and series they have worked in.

The most interesting page was the filter search results for media. We had to join it with the actor table to check if the actor is a part of a movie or not. We also provided multiple actor selection facility. This was enabled by joining our actor-movie table twice. This was the most interesting type of filtering in the project. Another interesting page was the review page where we had to make sure that the user had not reviewed that particular piece of media. So we had to first request the database to get all the reviews and check if the user had revied that media before. Then accordingly, we redirect the user to the appropriate places. Also, we used the "LIKE" matching for finding out the actor/movie the user was talking about. This was also very interesting.

