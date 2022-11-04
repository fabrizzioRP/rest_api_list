from .list.list import Lists, List, ExportList, ListElement, DownloadList
from .list.configlist import ConfigLists
from .list.campaignList import CampaignList
from .list.health import Health

def initialize_routes(api):
    

    #Endpoints configlists and lists#
    #RESPETAR ORDEN EN LAS RUTAS Y METODOS PARA QUE FUNCIONEN CORRECTAMENTE
    api.add_resource(Lists, '/list', endpoint='auth:api_lists:lists_all', defaults={'id_list': None},  methods=['GET','DELETE'])
    api.add_resource(Lists,  '/list', endpoint='auth:api_lists:list_post', methods=['POST',])
    api.add_resource(Lists, '/list/<id_list>', endpoint='auth:api_lists:list_one',  methods=['GET', 'PUT', 'DELETE'])
    api.add_resource(List, '/lista/<id_list>', endpoint='auth:api_lists:list', methods=['GET', 'PUT', 'DELETE'])
    api.add_resource(ExportList, '/export_list/<id_list>', endpoint='auth:api_lists:export_list', methods=['GET'])
    api.add_resource(ListElement, '/addElement', endpoint='auth:api_lists:addElement', methods=['POST'])

    api.add_resource(DownloadList, '/downloadList', endpoint='auth:api_lists:downloadList' ,  methods=['POST'])


    
    api.add_resource(ConfigLists,'/configlist', endpoint='auth:api_lists:configlists_all', defaults={'id_config': None},  methods=['GET','DELETE'])
    api.add_resource(ConfigLists,'/configlist', endpoint='auth:api_lists:configlist_post', methods=['POST',])
    api.add_resource(ConfigLists,'/configlist/<id_config>', endpoint='auth:api_lists:configlist_one',  methods=['GET', 'PUT', 'DELETE'])

    api.add_resource(CampaignList,'/campaignList', endpoint='auth:api_lists:campaignList',  methods=['GET'])

    api.add_resource(Health,'/health', endpoint='auth:api_bots:health', methods=['GET',])
