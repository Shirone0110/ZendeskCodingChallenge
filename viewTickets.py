import requests
from requests.structures import CaseInsensitiveDict
import pandas as pd

class TicketViewer:
    # initialize global variables
    base_url = ''
    headers = CaseInsensitiveDict()
    url = -1

    def create_df(self, tickets): 
        """
        This function receives a dictionary of tickets and turns
        it into a dataframe for viewing purposes. The function returns
        the dataframe.
        """
        col = ["id", "type", "subject", "status", "requester_id"]
        df = pd.DataFrame(columns = col) # create an empty dataframe with columns col
        for i in range(len(tickets)):
            # get the columns we want from the dictionary
            tmp = {new_key: tickets[i][new_key] for new_key in col}
            # append each row to the empty dataframe
            row = pd.DataFrame(tmp, index = [i])
            df = df.append(row)
        # set the index column to be the id number of the tickets
        df = df.set_index('id')
        df['requester_id'] = pd.to_numeric(df['requester_id'])
        return df

    def get_json_tickets(self, url): 
        """
        This function receievs a url to tickets.json file from the API
        and returns the tickets.json file to the program or -1 if there 
        is an error.
        """
        try:
            resp = requests.get(url, headers = self.headers)
            if (resp.status_code // 100) != 2: # if server returns an error
                print("An error was returned. Please try again later.\n")
                return -1
            return resp.json()
        except: # if server is not available
            print("The server is not available. Please try again later.\n")
            return -1

    def get_json_clients(self, url, auth):
        """
        This function receives a url to clients.json from the API with the 
        authentication to access the file and returns the clients.json file 
        to the program or -1 if there is an error.
        """
        try:
            resp = requests.get(url, auth = auth)
            if ((resp.status_code // 100) != 2): # if server returns an error
                print("An error was returned. Please try again later.\n")
                return -1
            return resp.json()
        except: # if server is not available
            print("The server is not available. Please try again later.\n")
            return -1

    def get_json_token(self, url, headers, data, auth): 
        """
        This function receives a url to token.json from the API with headers,
        data, and authentication to access the file and returns the token.json
        file to the program or -1 if there is an error.
        """
        try:
            resp = requests.post(url, headers = headers, json = data, auth = auth)
            if (resp.status_code // 100) != 2: # if server returns an error
                print("An error was returned. Please try again later.\n")
                return -1
            return resp.json()
        except: # if server is not available
            print("The server is not available. Please try again later.\n")
            return -1

    def get_valid_input(self, prev, next): 
        """
        This function will repeatedly prompt the user until it receives a 
        valid input. prev and next are booleans value indicating whether
        there is a previous or next ticket page respectively. The function
        returns the valid input.
        """
        prompt = """Select an option:
            1. Enter 1 to view all tickets
            2. Enter 2 to view a specific ticket
            3. Enter 3 to quit\n"""
        next_page = "\tEnter 'n' to go to the next ticket page\n"
        prev_page = "\tEnter 'p' to go to the previous ticket page\n"
        valid_ans = ['1', '2', '3'] # default valid answers 

        if (prev != 0): # if there is a previous page
            prompt += prev_page
            valid_ans.append('p')

        if (next != 0): # if there is a next page
            prompt += next_page
            valid_ans.append('n')
        
        # get input from user
        userinput = input(prompt)

        # repeat until get a valid input
        while (userinput not in valid_ans):
            print("Not a valid command. Please try again.")
            userinput = input(prompt)
        return userinput

    def view_single(self, df):
        """
        This function receives the dataframe consists of every ticket detail
        and return the detail of a single ticket or an error if there
        is no ticket with the given id.
        """
        # prompt the user for the ticket index
        index = int(input("Enter the id of the ticket you want to view\n"))

        try: # if there is a ticket with given index
            return df.loc[[index]]
        except KeyError: # if there is not, return error
            return "Sorry, there was no ticket with that id number\n"

    def init_url(self):
        """
        This function initialize a url list of ticket pages so that we can
        show which page we are on and easily go to the previous and next
        ticket page. It will return -1 if there is an error or the url list
        if there is no error.
        """
        url = []
        # url of the first page 
        url.append(f'{self.base_url}per_page=25&start_time=0')
        index = 0
        # get the json to get end_of_stream and after_url attribute
        json = self.get_json_tickets(url[0])
        if json == -1: # can't get json from the url
            return -1
        while (json["end_of_stream"] == False): # while not last page
            url.append(json["after_url"]) # append the next url
            index = index + 1 # increase index
            json = self.get_json_tickets(url[index]) # get json from the next url
        
        # return the url list
        self.url = url

    def get_credentials(self): 
        """
        This function get the user's credentials to connect to the API.
        First it will get the subdomain name, email, and api token of the 
        user to get the client list from the API.
        Then it will get the first client's id number to get the full token
        for that id number.
        The full token is what we need to access the tickets data.
        The function will return True if it successfully get the tickets data 
        and False otherwise.
        """
        # need subdomain name, email, and api token to get clients.json
        domain = input("Please enter your Zendesk subdomain name (without .zendesk.com): ")
        url = f'https://{domain}.zendesk.com/api/v2/oauth/clients.json'
        email = input("Please enter your email address: ")
        api_token = input("Please enter your API token: ")
        auth = (f'{email}/token', api_token)
        json = self.get_json_clients(url, auth)

        # if there was an error getting the json, return
        if json == -1:
            return False

        # get the client id from the json
        id = json["clients"][0]["id"]
        url = f'https://{domain}.zendesk.com/api/v2/oauth/tokens.json'
        # create header and data to get token.json
        header = CaseInsensitiveDict()
        header = {'Content-Type': "application/json"}
        data = {"token": {"client_id": str(id), "scopes": ["read", "write"]}}
        json = self.get_json_token(url, header, data, auth)

        # if there was an error getting the json, return
        if json == -1:
            return False

        # get the user's full token to access tickets
        full_token = json["token"]["full_token"]
        self.headers["Authorization"] = f"Bearer {full_token}"
        self.base_url = f'https://{domain}.zendesk.com/api/v2/incremental/tickets/cursor.json?'
        return True

def main():
    """
    This function will navigate the user while using the program,
    including getting user's credentials, getting user inputs, and
    displaying the information the user requests.
    """
    program = TicketViewer()
    # start the program
    print("Welcome to the ticket viewer.")
    # get user credentials
    if program.get_credentials() == False:
        return
    # get valid input when there's no previous and after page
    userinput = program.get_valid_input(0, 0)
    # initialize url list
    program.init_url()
    # if there's an error getting the url list
    # keep trying again until the user quits
    try:
        while (program.url == -1):
            print("Trying again ... Press any key to exit the program.\n")
            program.init_url()
    except KeyboardInterrupt:
        return
    
    # current page is the first page
    cur_page = 0
    # while not exit the program
    while (userinput != '3'):
        if userinput == 'n': # go to the next page
            cur_page = cur_page + 1
        elif userinput == 'p': # go to the previous page
            cur_page = cur_page - 1
        
        # if the user want a single ticket, we need every ticket index 
        # so we get every ticket in the account
        if userinput == '2': 
            json = program.get_json_tickets(f'{program.base_url}start_time=0')
        # else only get the json for the current page
        else:
            json = program.get_json_tickets(program.url[cur_page])

        if (json == -1): # there was an error 
            # get new user input
            userinput = program((cur_page > 0), (cur_page < len(url) - 1))
            # skip to the next loop
            continue

        # there was no error
        tickets = json["tickets"]

        if (len(tickets) == 0): # no ticket to view
            print("There are no tickets to view at this time.")
        else: # turn ticket dictionary into dataframe
            df = program.create_df(tickets)
        
        if (userinput == '2'): # if view a single ticket
            print(program.view_single(df))
        else: # view a ticket page
            print(df)
            # print out current page number
            print(f"You are viewing page {cur_page + 1} of {len(program.url)}")
        
        # get the next user input
        userinput = program.get_valid_input((cur_page > 0), 
                    (cur_page < len(program.url) - 1))

    # exit from the program
    print("Thank you for using the viewer. Bye!")

if __name__ == "__main__":
    main()

