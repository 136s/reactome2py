"""
Utility functions for Reactome data-fetch, mappings, and overlay networks in human.
"""
from requests.exceptions import ConnectionError
import requests
import io
import tarfile
import zipfile


def ehld_stids():
    """
    Retrieves a list of high-level hierarchy pathway with Enhanced High Level Diagrams (EHLD) https://reactome.org/icon-info/ehld-specs-guideline

    :return: list of pathway stIds
    """

    url = "https://reactome.org/download/current/ehld/svgsummary.txt"

    try:
        response = requests.get(url=url)
    except ConnectionError as e:
        print(e)

    if response.status_code == 200:
        content_list = response.text.splitlines()
        st_ids = [stId for stId in content_list if 'R-' in stId]
        return st_ids
    else:
        print('Status code returned a value of %s' % response.status_code)


def sbgn_stids():
    """
    Retieves a list of lower-level (with hierarchy) pathways that have SBGNs https://reactome.org/about/news/110-sbgn-files-revamp

    :return: list of pathway stIds
    """

    url = "https://reactome.org/download/current/homo_sapiens.sbgn.tar.gz"

    try:
        response = requests.get(url=url)
    except ConnectionError as e:
        print(e)

    if response.status_code == 200:
        tar_file = tarfile.open(fileobj=io.BytesIO(response.content))
        file_names = tar_file.getnames()
        ehlds = ehld_stids()
        sbgns = [f.replace('.sbgn', '') for f in file_names]
        sbgn_only = list(set(sbgns) - set(ehlds))
        return sbgn_only
    else:
        print('Status code returned a value of %s' % response.status_code)


def _yield_zip(response):
    """
    Read zipfile in memory https://docs.python.org/3/library/zipfile.html

    :param response:
    :return: content of zip file
    """

    with zipfile.ZipFile(io.BytesIO(response.content)) as the_zip:
        for zip_info in the_zip.infolist():
            with the_zip.open(zip_info) as the_file:
                yield the_file.readlines()


def _read_ziplines(response):
    """
    Helper function to clean zipline content parsing

    :param response:
    :return: list
    """

    return [c.split('\t') for c in [c.decode('utf8') for c in list(_yield_zip(response))[0]]]


def gene_mappings():
    """
    Maps reactome pathway stId and name to it's associated gene list (HGNC)

    :return: dictionary of reactome pathways and HGNC gene mappings to the pathway.
    """

    url = "https://reactome.org/download/current/ReactomePathways.gmt.zip"

    try:
        response = requests.get(url=url)
    except ConnectionError as e:
        print(e)

    if response.status_code == 200:
        gm = _read_ziplines(response)
        relations = []

        for i, e in enumerate(gm):
            gm[i] = [s.strip() for s in gm[i]]
            d = dict(name=gm[i][0], stId=gm[i][1], genes=gm[i][2:len(gm[i])])
            relations.append(d)

        return relations
    else:
        print('Status code returned a value of %s' % response.status_code)


def pathway_fi(stId="R-HSA-177929", pattern="R-HSA-"):
    """
    :param stId:
    :param pattern:

    :return: json
    """

    headers = {
        'accept': 'application/json',
    }

    if pattern in stId:
        stId = stId.replace(pattern, "")

    url = "http://cpws.reactome.org/caBigR3WebApp2018/FIService/network/convertPathwayToFIs/%s" % stId

    try:
        response = requests.get(url=url, headers=headers)
    except ConnectionError as e:
        print(e)

    if response.status_code == 200:
        return response.json()
    else:
        print('Status code returned a value of %s' % response.status_code)


def pathway_boolean_network(stId="R-HSA-177929", pattern="R-HSA-"):
    """
    :param stId:
    :param pattern:

    :return: json
    """

    headers = {
        'accept': 'application/json',
    }

    if pattern in stId:
        stId = stId.replace(pattern, "")

    url = "http://cpws.reactome.org/caBigR3WebApp2018/FIService/network/convertPathwayToBooleanNetwork/%s" % stId

    try:
        response = requests.get(url=url, headers=headers)
    except ConnectionError as e:
        print(e)

    if response.status_code == 200:
        return response.json()
    else:
        print('Status code returned a value of %s' % response.status_code)


def pathway_factor_graph(stId="R-HSA-177929", pattern="R-HSA-"):
    """
    :param stId:
    :param pattern:

    :return: json
    """

    headers = {
        'accept': 'application/json',
    }

    if pattern in stId:
        stId = stId.replace(pattern, "")

    url = "http://cpws.reactome.org/caBigR3WebApp2018/FIService/network/convertPathwayToFactorGraph/%s" % stId

    try:
        response = requests.post(url=url, headers=headers)
    except ConnectionError as e:
        print(e)

    if response.status_code == 200:
        return response.json()
    else:
        print('Status code returned a value of %s' % response.status_code)


def drug_data_source(source="drugcentral"):
    """
    Query a list of drug-target interactions.

    :param source: drugcentral or targetome

    :return: json
    """

    headers = {
        'accept': 'application/json',
    }

    url = "http://cpws.reactome.org/caBigR3WebApp2018/FIService/drug/listDrugs/%s" % source

    try:
        response = requests.get(url=url, headers=headers)
    except ConnectionError as e:
        print(e)

    if response.status_code == 200:
        return response.json()
    else:
        print('Status code returned a value of %s' % response.status_code)


def drug_target_interactions(ids="EGFR\nESR1\nBRAF", source="drugcentral"):
    """
    :param ids: Gene HGNC seperated by new line
    :param source: drugcentral or targetome

    :return: json
    """

    headers = {
        'accept': 'application/json',
    }

    data = ids

    url = "http://cpws.reactome.org/caBigR3WebApp2018/FIService/drug/queryDrugTargetInteractions/%s" % source

    try:
        response = requests.post(url=url, headers=headers, data=data)
    except ConnectionError as e:
        print(e)

    if response.status_code == 200:
        return response.json()
    else:
        print("Status code returned a value of %s" % response.status_code)


def drug_target_interaction_pe_in_diagram(source="drugcentral", pdId="507988", peId="1220578"):
    """
    Query drug/target interactions for a PE that is specified by its pdId

    :param source: drugcentral or targetome
    :param pdId:
    :param peId:

    :return: json
    """

    headers = {
        'accept': 'application/json',
    }

    ids = "/".join([pdId, peId])

    url = "http://cpws.reactome.org/caBigR3WebApp2018/FIService/drug/queryInteractionsForPEInDiagram/%s/%s" % (source, ids)

    try:
        response = requests.get(url=url, headers=headers)
    except ConnectionError as e:
        print(e)

    if response.status_code == 200:
        return response.json()
    else:
        print('Status code returned a value of %s' % response.status_code)


def drug_target_interaction_diagram(source="drugcentral", pdId="507988"):
    """
    Query drug/target interactions for a PE by pdId.

    :param source: drugcentral or targetome
    :param pdId:

    :return: json
    """

    headers = {
        'accept': 'application/json',
    }

    url = "http://cpws.reactome.org/caBigR3WebApp2018/FIService/drug/queryInteractionsForDiagram/%s/%s" % (source, pdId)

    try:
        response = requests.get(url=url, headers=headers)
    except ConnectionError as e:
        print(e)

    if response.status_code == 200:
        return response.json()
    else:
        print('Status code returned a value of %s' % response.status_code)
