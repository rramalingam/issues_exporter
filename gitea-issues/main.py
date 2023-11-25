import giteapy
import csv

configuration = giteapy.Configuration()

# ======================================================================================================================
# Modify configuration for your needs
configuration.host = 'https://<your org gitea instance>/api/v1'
configuration.api_key['access_token'] = '<above instance access token here>'  # https://<YOUR GITEA URL ORIGIN>/user/settings/applications
my_organization_name = '<project name>'
#you can list your repos that you need to export
my_repo_name1 = '<repo_name1>'
my_repo_name2 = '<repo_name2>'
my_repo_name3 = '<repo_name3>'
# ======================================================================================================================

api_client = giteapy.ApiClient(configuration)
issues_api_instance = giteapy.IssueApi(giteapy.ApiClient(configuration))

def convert_list_to_str (label_arr):
    str1 = ""
    for rec in label_arr:
        str1 += rec.name
        str1 += ","

    # return string
    return str1

def dump_to_csv(filename, array_of_objects):
    # we need to create list of dicts with custom properties from list of api objects fields
    #print(array_of_objects)
    converted = list(
        map(lambda x: {'Title': x.title, 'Description': x.body, 'URL': x.url, 'Milestone': x.milestone is None or (x.milestone.title),
                       'Label': x.labels is None or (convert_list_to_str(x.labels))},
            array_of_objects))  # could be used vars(x) to convert all

    # this is just to avoid duplicates
    array_of_dicts = []
    map_info = {}
    for conv in converted:
        if conv['Title'] not in map_info:
            array_of_dicts.append(conv)
            map_info[conv['Title']] = True

    keys = array_of_dicts[0].keys()

    with open(filename, 'w', newline='') as output_file:
        output_file.seek(0)
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(array_of_dicts)


def fetch_all(**kwargs):
    result = []
    page = 1
    while True:
        fetched = issues_api_instance.issue_list_issues(**kwargs, page=page)
        if len(fetched) == 0:
            break
        result += fetched
        page += 1

    return result


def export_open_closed_issues(organization_name, repository_name):
    open_issues = fetch_all(owner=organization_name, repo=repository_name, state='open')
    # we need to filter issues that are not feature branches merged into main branch
    closed_issues = list(filter(lambda x: x.pull_request is None or (not x.pull_request.merged),
                                fetch_all(owner=organization_name, repo=repository_name, state='closed')))

    dump_to_csv(repository_name+'_open_issues.csv', open_issues)
    dump_to_csv(repository_name+'_closed_issues.csv', closed_issues)


if __name__ == '__main__':
    print('starting..')
    export_open_closed_issues(organization_name=my_organization_name, repository_name=my_repo_name1)
    export_open_closed_issues(organization_name=my_organization_name, repository_name=my_repo_name2)
    export_open_closed_issues(organization_name=my_organization_name, repository_name=my_repo_name3)
    print('done.')
