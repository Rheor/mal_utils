#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from bs4 import BeautifulSoup
import requests
import argparse
from jikanpy import Jikan, exceptions

jikan = Jikan()

USERNAME = "Rheor"


GENRES_IDS = {
    "action": 1,
    "adventure": 2,
    "cars": 3,
    "comedy": 4,
    "dementia": 5,
    "demons": 6,
    "mystery": 7,
    "drama": 8,
    "ecchi": 9,
    "fantasy": 10,
    "game": 11,
    "hentai": 12,
    "historical": 13,
    "horror": 14,
    "kids": 15,
    "magic": 16,
    "martial_arts": 17,
    "mecha": 18,
    "music": 19,
    "parody": 20,
    "samurai": 21,
    "romance": 22,
    "school": 23,
    "sci-fi": 24,
    "shoujo": 25,
    "shoujo_ai": 26,
    "shounen": 27,
    "shounen_ai": 28,
    "space": 29,
    "sports": 30,
    "super_power": 31,
    "vampire": 32,
    "yaoi": 33,
    "yuri": 34,
    "harem": 35,
    "slice_of_life": 36,
    "supernatural": 37,
    "military": 38,
    "police": 39,
    "psychological": 40,
    "thriller": 41,
    "seinen": 42,
    "josei": 43
}


GENRE_COUNTERS = {genre: 0 for genre, genre_id in GENRES_IDS.items()}


def _genres_from_anime(anime_url):
    soup = BeautifulSoup(requests.get(anime_url).text, "html.parser")
    genres = soup.find_all(
        lambda tag: "/anime/genre" in tag.attrs.get("href", ""))
    genres = list(map(lambda tag_genre: "_".join(
        tag_genre.attrs["title"].split(" ")).lower(), genres))

    return genres


def generate_recommandations(username):

    try:
        my_anime_list = jikan.user(
            username=username, request='animelist', argument='completed')["anime"]
    except exceptions.APIException as err:
        print("Encountered error while fething jikanpy API : {}".format(err))
        exit(1)

    my_animes_genres = list(map(lambda anime: _genres_from_anime(anime["url"]),
                                my_anime_list))

    for anime_genres in my_animes_genres:
        for genre in anime_genres:
            GENRE_COUNTERS[genre] += 1

    prefered_genres = sorted(GENRE_COUNTERS.items(),
                             key=lambda genre_counter: genre_counter[1],
                             reverse=True)[:25]

    recommandations = list(
        map(lambda genre: jikan.search('anime', '', parameters={
            'genre': GENRES_IDS[genre[0]]})["results"],
            prefered_genres))

    recommandations = [item for sublist in recommandations for item in sublist]

    recommandations = list(
        map(
            lambda recommandation: {
                "title": recommandation["title"],
                "score": recommandation["score"],
                "url": recommandation["url"]
            },
            recommandations))

    recommandations = list(set(tuple(d.items()) for d in recommandations))

    recommandations = [dict(t) for t in recommandations]

    recommandations = list(
        filter(lambda recommandation: recommandation["score"] > 7.5,
               recommandations))

    recommandations = sorted(recommandations,
                             key=lambda rec: rec["score"],
                             reverse=True)

    with open("result.json", "w+") as f:
        f.write(json.dumps(recommandations))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate some recommandations based on prefered genres")
    parser.add_argument(
        "-u", "--username", help="My anime list username", required=True)
    args = parser.parse_args()
    generate_recommandations(args.username)
