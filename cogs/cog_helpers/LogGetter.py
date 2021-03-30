from requests_oauthlib import OAuth2Session
import json
import pyxivapi
import base64
import asyncio.exceptions
from aiohttp import ClientSession, ClientTimeout

#query templates are saved in files to be more readable
class LogGetter:

    def __init__(self):
        #ids stored as (zone id, encounter id)
        self.encounter_ids = {"tea": (32, 1050), "ucob_sb": (19, 1039), "uwu_sb": (23, 1042),
                              "ucob_shb": (30, 1047), "uwu_shb": (30, 1048), "e12s": (38, 77)}
        self.server_regions = {"sargatanas": "na", "gilgamesh": "na"}

        #get oauth2 token and client_id from file
        t = ""
        fp = "C:/Users/stefa/PycharmProjects/moxic_bot/Authentication Files/FFlogs Authentication.txt"
        with open(fp, "r") as file:
            for i in range(6):
                t += file.readline()
            client_id = file.readline()
            xiv_api_key = file.readline()
            self.fflogs_url = file.readline()
        token = json.loads(t)

        timeout = ClientTimeout(total=7.5)
        self.session = OAuth2Session(client_id, token=token)
        self.xiv_api_client = pyxivapi.XIVAPIClient(api_key=xiv_api_key, session=ClientSession(timeout=timeout))

    #encounter is the page with all of your logs
    async def get_logs_by_encounter(self, encounter=None, encounter_id=None, name=None, server=None, id=None):
        if id is not None:
            with open("./fflogs_queries/get_fight_logs_by_id.txt", "r") as f:
                q = f.read()

            if not encounter_id: encounter_id = self.encounter_ids[encounter][1]
            return await self.get_query_results(q.format(character_id=id,
                                                         encounter_id=encounter_id))

        elif name is not None and server is not None:
            with open("./fflogs_queries/get_fight_logs.txt", "r") as f:
                q = f.read()

            if not encounter_id: encounter_id = self.encounter_ids[encounter][1]
            return await self.get_query_results(q.format(name=name,
                                                         server=server,
                                                         region=self.server_regions[server],
                                                         encounter_id=encounter_id))

        else:
            raise Exception("Need either name and server or id to lookup character")

    async def get_main_page_logs(self, name=None, server=None, id=None):
        if id is None:
            with open("./fflogs_queries/get_main_page.txt", "r") as f:
                q = f.read()

            return await self.get_query_results(q.format(name=name,
                                                         server=server,
                                                         region=self.server_regions[server]))
        elif id is not None:
            with open("./fflogs_queries/get_main_page_by_id.txt", "r") as f:
                q = f.read()

                return await self.get_query_results(q.format(id=id))

    async def get_fflogs_id(self, name, server):
        with open("./fflogs_queries/get_id.txt", "r") as f:
            q = f.read()

        tmp = await self.get_query_results(q.format(name=name,
                                                     server=server,
                                                     region="na",
                                                     id_type="canonical"))

        return tmp['data']['characterData']['character']['canonicalID']

    async def get_lodestone_id(self, name, server):
        with open("./fflogs_queries/get_id.txt", "r") as f:
            q = f.read()

        tmp =  await self.get_query_results(q.format(name=name,
                                                     server=server,
                                                     region="na",
                                                     id_type="lodestone"))

        return tmp['data']['characterData']['character']['lodestoneID']

    async def get_query_results(self, query):
        return self.session.get(self.fflogs_url, json={"query": query}).json()

    async def get_lodestone_data(self, lodestone_id):
        for i in range(5):
            try:
                print(f"Attempt number {i + 1}")
                lodestone = await self.xiv_api_client.character_by_id(
                    lodestone_id=lodestone_id
                )
                break
            except asyncio.exceptions.TimeoutError:
                if i == 4: raise NoLodestoneData
                print("Timed out trying again")

        print(lodestone)
        return (base64.b64encode((json.dumps(lodestone)).encode())).decode()

    async def get_reports_page(self, report_id):
        with open("./fflogs_queries/get_reports_rankings.txt", "r") as f:
            q = f.read()

        tmp =  await self.get_query_results(q.format(report_id=report_id))

        return tmp['data']['reportData']['report']['rankings']['data']

    def close_connections(self):
        self.session.close()
        #await self.xiv_api_client.session.close()