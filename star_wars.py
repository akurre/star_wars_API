# =====================================================================================================================
# =============================================== IMPORT STATEMENTS====================================================
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import json


# =====================================================================================================================
# ================================================= USER CONTROLS =====================================================
get_full_jsons = False       # select True to show full json instead of links to subject


# =====================================================================================================================
# ================================================ GLOBAL VARIABLES ===================================================
swapi_films_url = 'https://swapi.dev/api/films/'
swapi_chars_url = 'https://swapi.dev/api/people/'
swapi_planets_url = 'http://swapi.dev/api/planets/'


# =====================================================================================================================
# =================================================== FUNCTIONS =======================================================
def get_url_dict(input_json):
    """ obtains the URL key from a json dictionary and returns another dictionary with format url: json"""
    url_keys = {}
    for json in input_json:
        key = json['url']
        url_keys[key] = json
    return url_keys


def replace_url(list_all, needed_url_keys):
    """ replaces the url for a person, planet, etc entry with the descriptive json belonging to it """
    for json in list_all:
        for key, value in json.items():
            if isinstance(value, list):     # if there are multiples
                try:
                    # get() returns value for spec key if key exists
                    json[key] = ([needed_url_keys.get(x, x) for x in value])
                except TypeError:   # in case of dict within
                    pass    
            elif isinstance(value, dict):
                pass    # in case already converted with function 
        json['image'] = 'https://live.staticflickr.com/8688/17109875941_3d91f9c09c_b.jpg'
    return list_all


def get_json_response(url_input):
    """ gets a response from the API """
    # json.loads take a string as input and returns a dictionary as output.
    # json.dumps take a dictionary as input and returns a string as output.
    response = requests.get(url_input)
    response_json = response.json()
    returned_json = (json.dumps(response_json, indent=4, sort_keys=False))
    returned_json = (json.loads(returned_json))['results']
    return returned_json


def replace_keys(returned_json, key_input_json):
    """ takes the returned_json and replaces urls with the corresponding character, planet, or film """
    url_x_keys = get_url_dict(input_json=key_input_json)
    altered_json = replace_url(list_all=returned_json, needed_url_keys=url_x_keys)
    return altered_json


def get_styles(file):
    """ reads in css styling """
    output = '<!DOCTYPE html><html><head><style>'
    with open(file, 'r') as f:
        output += f.read()
    output += '</style></head><body>'
    return output


def get_full_list(category, json_all, pronoun, naming):
    """ returns an html str output of a list of items in a certain category (characters, planets, etc) to display on a
    corresponding endpoint, incl links to a desired subject """
    output = get_styles(file='styles_general.html')
    output += f'<center><h1>Star Wars {category.title()}</h1>'  # h1 stands for header1, </> ends
    output += f'<p>Please click on a {str(category).lower()} below to obtain information about {pronoun}.<br><br></p>'
    for indiv_dict in json_all:     # get names of specific items in category
        spec_name = indiv_dict[naming]      # get name/title
        output += f'<br><a href="/{category}/{spec_name}_{category[:-1]}"> {spec_name} </a><br>'
    output += '<footer><h2><a href="/">Return Home</a></h2><p>By Ashlen Kurre</p></footer></body></center></html>'
    return output


def get_specific(spec_name, alt_category, json, naming):
    """ returns an html str output that lists the details of a desired subject, including links to subjects that may be
     covered by the API """
    result = {}
    output = get_styles('styles_specific.html')
    output += f'<h1>{spec_name}</h1>'  # h1 stands for header1, </> ends
    for wanted_json in json:
        if spec_name == wanted_json[naming]:
            result = wanted_json
            break
    for key, value in result.items():
        if value:
            if not get_full_jsons:
                if isinstance(value, list):
                    values = []
                    for potential_dict in value:  # value was list of dicts or list of strings
                        try:    # if dict entry
                            values.append(potential_dict['title'])
                            alt_category = 'films'
                        except KeyError:    # in case it's 'title' vs 'name'
                            values.append(potential_dict['name'])
                        except TypeError:   # if string
                            values.append(potential_dict)
                    if key.lower() == 'characters':     # this is hacky but ran out of time
                        alt_category = 'characters'
                    if key.lower() == 'planets':
                        alt_category = 'planets'
                    values = [f'<a href="/{alt_category}/{x.replace(" ", "%20")}_{alt_category[:-1]}">{x.title()}</a>' 
                              for x in values]

                    output += f'<p><b>{str(key).title().replace("_", " ")}</b> --- {", ".join(values)}</p>'
                else:
                    output += f'<p><b>{str(key).title().replace("_", " ")}</b> --- {str(value).title()}</p>'
            else:
                output += f'<p><b>{str(key).title().replace("_", " ")}</b> --- {str(value).title()}</p>'

    output += '<footer><h2><div id="bot"><center><a href="/">Return Home</a></div></h2><center><p>By Ashlen Kurre</p>' \
              '</footer></center></body></html>'  # would have put this into a .html file but time didn't permit
    return output


def main():
    PORT = 8000
    server = HTTPServer(('', PORT), requestHandler)  # first thing is instance of the server class (first is tuple host
    # name, blank because we're serving on local host. Second is port number). Then it is the request handler

    print(f'Server running on port {PORT}')
    server.serve_forever()  # this method starts a server and runs until it is stopped with ctrl+c in terminal


# =====================================================================================================================
# =================================================== CLASSES =========================================================
class requestHandler(BaseHTTPRequestHandler):  # takes the webaddress path and displays it in the browser

    def set_headers(self):
        self.send_response(200)  # send back a response (200=success)
        self.send_header('content-type', 'text/html')  # details content type which the webpage will display
        self.end_headers()  # must close headers once all are listed

    def do_GET(self):
        # get the API response for each category
        planets_json = get_json_response(url_input=swapi_planets_url)
        people_json = get_json_response(url_input=swapi_chars_url)
        films_json = get_json_response(url_input=swapi_films_url)
        
        # ===================== HOME PAGE =====================
        if self.path == '/':
            self.set_headers()
            with open('index.html', 'r') as f:
                output = f.read()

            self.wfile.write(output.encode())   # wfile = writable file. Encode() converts str into bytes, shows as str

        # ===================== PLANETS =====================
        if self.path.endswith('/planets'):  # endswith takes the end of a string (path)
            self.set_headers()

            output = get_full_list(category='planets', json_all=planets_json, pronoun='it', naming='name')

            self.wfile.write(output.encode())

        if self.path.endswith('_planet'):
            self.set_headers()

            planet_name = self.path.split('/')[2].split('_')[0].replace("%20", " ")
            planets_json = replace_keys(returned_json=planets_json, key_input_json=people_json)
            planets_json = replace_keys(returned_json=planets_json, key_input_json=films_json)
            output = get_specific(spec_name=planet_name, alt_category='characters', json=planets_json, naming='name')

            self.wfile.write(output.encode())

        # ===================== CHARACTERS =====================
        if self.path.endswith('/characters'):  # endswith takes the end of a string (path)
            self.set_headers()

            output = get_full_list(category='characters', json_all=people_json, pronoun='them', naming='name')

            self.wfile.write(output.encode())

        if self.path.endswith('_character'):
            self.set_headers()

            char_name = self.path.split('/')[2].split('_')[0].replace("%20", " ")
            people_json = replace_keys(returned_json=people_json, key_input_json=planets_json)
            people_json = replace_keys(returned_json=people_json, key_input_json=films_json)
            output = get_specific(spec_name=char_name, alt_category='planets', json=people_json, naming='name')

            self.wfile.write(output.encode())

        # ===================== FILMS =====================
        if self.path.endswith('/films'):  # endswith takes the end of a string (path)
            self.set_headers()

            output = get_full_list(category='films', json_all=films_json, pronoun='it', naming='title')

            self.wfile.write(output.encode())

        if self.path.endswith('_film'):
            self.set_headers()

            film_name = self.path.split('/')[2].split('_')[0].replace("%20", " ")
            films_json = replace_keys(returned_json=films_json, key_input_json=planets_json)
            films_json = replace_keys(returned_json=films_json, key_input_json=people_json)
            output = get_specific(spec_name=film_name, alt_category='characters', json=films_json, naming='title')

            self.wfile.write(output.encode())

        if not self.path.endswith(('_film', '/films', '_character', '/characters', '_planet', '/planets', '/')):
            # this is hacky, but unfortunately the footer messed with the error page here and I wanted an excuse to
            # grace you with JarJar Binks

            # ===================== ERRORS =====================
            self.send_response(404)  # send back a response (200=success)
            self.send_header('content-type', 'text/html')  # details content type which the webpage will display
            self.end_headers()  # must close headers once all are listed
            output = get_styles(file='styles_general.html')
            output += '<center><br><h1>404 Error: Page not found.</h1><br>' \
                      '<h1>Sorry, your spaceship is in the wrong galaxy!</h1><br><br>' \
                      '<img src="https://i.imgur.com/FpkCcc0.jpg" class="icons"></a></center>'
            output += '<footer><h2><center><a href="/">Return Home</a></h2><center><p>By Ashlen Kurre</p></footer>' \
                      '</center></body></html>'
            self.wfile.write(output.encode())


# =====================================================================================================================
# ================================================== RUN CODE =========================================================
if __name__ == '__main__':  # if this python file is being run directly, not an imported module
    main()
