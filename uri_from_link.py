import spotify_uri

url = input("Enter the spotify link: ")
try:
	spotify_object = spotify_uri.parse(url)
	uri = spotify_object.toURI()
	print(uri)
except Exception as e:
	print(f"Incorrect url {e}")
