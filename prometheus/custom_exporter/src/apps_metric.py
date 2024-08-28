
# Default's python library
import json

# Third parties libraries
import requests

# Internal modules
import utils
import logsystem

LOG = logsystem.get_logger(__name__)

def apps_metric(url,username='',password=''):


    # None or '' will result as False in this boolean expression
    if not url or not username or not password:
        len_password = 0 if password is None else len(password)
        LOG.error(f"parameter None or empty: url={url} or username={username} or len(password)={len_password}")
        return dict(
            name="number_of_apps",
            value=-1.0,
            documentation="Number of installed apps",
            sub_metric_labels=[],
            sub_metric_values=[]
        )

    LOG.debug(f"parameters: url={url} or username={username} or len(password)={len(password)}")

    if url=='test-empty':
        invoke_rest_service=retrieve_fake_data_empty
    elif url=='test':
        invoke_rest_service=retrieve_fake_data
    else:
        invoke_rest_service=retrieve_data

    try:
        resp=invoke_rest_service(url,username,password)
        response_json=json.loads(resp)
        if 'appInstances' in response_json:
            LOG.debug('Found "appInstances" in response')
            num_of_apps = len(response_json['appInstances'])
        elif 'status' in response_json and response_json['status'] == 404:
            LOG.debug('Found "status"==404 in response')
            num_of_apps=0
        else:
            LOG.error("Unexpected fields in the JSON", exc_info=True)
            LOG.error(resp)
            raise Exception('Error: json with unexpected fields')
        value=float(num_of_apps)
    except Exception as e:
        LOG.error('Count of rApps failed due to an unexpected error', exc_info=True)
        value=-1.0

    return dict(
        name="number_of_apps",
        value=value,
        documentation="Number of installed apps",
        sub_metric_labels=[],
        sub_metric_values=[]
    )


def retrieve_data(url, username, password, timeout=2):

    # LOGIN TOKEN RETRIVEAL
    # url = "https://appmgr.662502336946.eu-west-1.ac.ericsson.se/auth/v1/login"
    url_dict=utils.analyze_url(url)
    auth_url=url_dict['proto']+'://'+url_dict['hostname']+'/auth/v1/login'

    response=requests.request("POST",auth_url,
                                headers={
                                    'X-Login': username,
                                    'X-Password': password
                                },
                                data={},
                                verify=False,
                                timeout=timeout)
    login_token=response.text

    # INVOKE THE WEB SERVICE
    # url = "https://appmgr.662502336946.eu-west-1.ac.ericsson.se/app-manager/onboarding/v1/apps"

    headers={ 'Cookie': 'JSESSIONID='+login_token }
    response=requests.request("GET",url,headers=headers,data={},verify=False,timeout=timeout)

    return response.text

def retrieve_fake_data_empty(url, username, password):
    return '{"type":"Not Found","title":"Not Found","status":404,"detail":"App Instances not found","appLcmErrorCode":1001,"appLcmErrorMessage":"Could not find the app instance specified.","url":"/app-lcm/v1/app-instances"}'

def retrieve_fake_data(url, username, password):
    return FAKE_DATA

FAKE_DATA='''
{
  "appInstances": [
    {
      "id": 16,
      "appOnBoardingAppId": 1,
      "healthStatus": "INSTANTIATED",
      "targetStatus": "INSTANTIATED",
      "createdTimestamp": "2022-10-25T11:33:39.140689Z[UTC]",
      "additionalParameters": "{}",
      "links": [
        {
          "rel": "self",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/16"
        },
        {
          "rel": "artifact-instances",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/16/artifact-instances"
        },
        {
          "rel": "app",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/1"
        },
        {
          "rel": "artifacts",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/1/artifacts"
        }
      ]
    },
    {
      "id": 17,
      "appOnBoardingAppId": 2,
      "healthStatus": "INSTANTIATED",
      "targetStatus": "INSTANTIATED",
      "createdTimestamp": "2022-10-25T12:24:38.275648Z[UTC]",
      "additionalParameters": "{}",
      "links": [
        {
          "rel": "self",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/17"
        },
        {
          "rel": "artifact-instances",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/17/artifact-instances"
        },
        {
          "rel": "app",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/2"
        },
        {
          "rel": "artifacts",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/2/artifacts"
        }
      ]
    },
    {
      "id": 18,
      "appOnBoardingAppId": 3,
      "healthStatus": "INSTANTIATED",
      "targetStatus": "INSTANTIATED",
      "createdTimestamp": "2022-10-25T12:38:12.425788Z[UTC]",
      "additionalParameters": "{}",
      "links": [
        {
          "rel": "self",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/18"
        },
        {
          "rel": "artifact-instances",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/18/artifact-instances"
        },
        {
          "rel": "app",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/3"
        },
        {
          "rel": "artifacts",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/3/artifacts"
        }
      ]
    },
    {
      "id": 11,
      "appOnBoardingAppId": 5,
      "healthStatus": "TERMINATED",
      "targetStatus": "TERMINATED",
      "createdTimestamp": "2022-10-24T08:21:34.635658Z[UTC]",
      "additionalParameters": "{}",
      "links": [
        {
          "rel": "self",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/11"
        },
        {
          "rel": "artifact-instances",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/11/artifact-instances"
        },
        {
          "rel": "app",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/5"
        },
        {
          "rel": "artifacts",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/5/artifacts"
        }
      ]
    },
    {
      "id": 2,
      "appOnBoardingAppId": 3,
      "healthStatus": "TERMINATED",
      "targetStatus": "TERMINATED",
      "createdTimestamp": "2022-10-11T17:26:07.775671Z[UTC]",
      "additionalParameters": "{}",
      "links": [
        {
          "rel": "self",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/2"
        },
        {
          "rel": "artifact-instances",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/2/artifact-instances"
        },
        {
          "rel": "app",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/3"
        },
        {
          "rel": "artifacts",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/3/artifacts"
        }
      ]
    },
    {
      "id": 5,
      "appOnBoardingAppId": 4,
      "healthStatus": "TERMINATED",
      "targetStatus": "TERMINATED",
      "createdTimestamp": "2022-10-12T11:13:58.975691Z[UTC]",
      "additionalParameters": "{}",
      "links": [
        {
          "rel": "self",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/5"
        },
        {
          "rel": "artifact-instances",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/5/artifact-instances"
        },
        {
          "rel": "app",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/4"
        },
        {
          "rel": "artifacts",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/4/artifacts"
        }
      ]
    },
    {
      "id": 10,
      "appOnBoardingAppId": 2,
      "healthStatus": "TERMINATED",
      "targetStatus": "TERMINATED",
      "createdTimestamp": "2022-10-20T11:07:57.246631Z[UTC]",
      "additionalParameters": "{}",
      "links": [
        {
          "rel": "self",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/10"
        },
        {
          "rel": "artifact-instances",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/10/artifact-instances"
        },
        {
          "rel": "app",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/2"
        },
        {
          "rel": "artifacts",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/2/artifacts"
        }
      ]
    },
    {
      "id": 1,
      "appOnBoardingAppId": 2,
      "healthStatus": "TERMINATED",
      "targetStatus": "TERMINATED",
      "createdTimestamp": "2022-10-11T15:44:56.856809Z[UTC]",
      "additionalParameters": "{}",
      "links": [
        {
          "rel": "self",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/1"
        },
        {
          "rel": "artifact-instances",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/1/artifact-instances"
        },
        {
          "rel": "app",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/2"
        },
        {
          "rel": "artifacts",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/2/artifacts"
        }
      ]
    },
    {
      "id": 15,
      "appOnBoardingAppId": 2,
      "healthStatus": "TERMINATED",
      "targetStatus": "TERMINATED",
      "createdTimestamp": "2022-10-25T11:12:01.330229Z[UTC]",
      "additionalParameters": "{}",
      "links": [
        {
          "rel": "self",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/15"
        },
        {
          "rel": "artifact-instances",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/15/artifact-instances"
        },
        {
          "rel": "app",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/2"
        },
        {
          "rel": "artifacts",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/2/artifacts"
        }
      ]
    },
    {
      "id": 4,
      "appOnBoardingAppId": 4,
      "healthStatus": "FAILED",
      "targetStatus": "INSTANTIATED",
      "createdTimestamp": "2022-10-12T11:12:39.189279Z[UTC]",
      "additionalParameters": "{}",
      "links": [
        {
          "rel": "self",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/4"
        },
        {
          "rel": "artifact-instances",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/4/artifact-instances"
        },
        {
          "rel": "app",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/4"
        },
        {
          "rel": "artifacts",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/4/artifacts"
        }
      ]
    },
    {
      "id": 3,
      "appOnBoardingAppId": 1,
      "healthStatus": "TERMINATED",
      "targetStatus": "TERMINATED",
      "createdTimestamp": "2022-10-11T17:29:49.883367Z[UTC]",
      "additionalParameters": "{}",
      "links": [
        {
          "rel": "self",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/3"
        },
        {
          "rel": "artifact-instances",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/3/artifact-instances"
        },
        {
          "rel": "app",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/1"
        },
        {
          "rel": "artifacts",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/1/artifacts"
        }
      ]
    },
    {
      "id": 6,
      "appOnBoardingAppId": 2,
      "healthStatus": "TERMINATED",
      "targetStatus": "TERMINATED",
      "createdTimestamp": "2022-10-13T12:07:24.477881Z[UTC]",
      "additionalParameters": "{}",
      "links": [
        {
          "rel": "self",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/6"
        },
        {
          "rel": "artifact-instances",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/6/artifact-instances"
        },
        {
          "rel": "app",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/2"
        },
        {
          "rel": "artifacts",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/2/artifacts"
        }
      ]
    },
    {
      "id": 14,
      "appOnBoardingAppId": 1,
      "healthStatus": "TERMINATED",
      "targetStatus": "TERMINATED",
      "createdTimestamp": "2022-10-25T11:07:22.638065Z[UTC]",
      "additionalParameters": "{}",
      "links": [
        {
          "rel": "self",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/14"
        },
        {
          "rel": "artifact-instances",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/14/artifact-instances"
        },
        {
          "rel": "app",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/1"
        },
        {
          "rel": "artifacts",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/1/artifacts"
        }
      ]
    },
    {
      "id": 8,
      "appOnBoardingAppId": 5,
      "healthStatus": "TERMINATED",
      "targetStatus": "TERMINATED",
      "createdTimestamp": "2022-10-17T13:51:13.438377Z[UTC]",
      "additionalParameters": "{}",
      "links": [
        {
          "rel": "self",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/8"
        },
        {
          "rel": "artifact-instances",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/8/artifact-instances"
        },
        {
          "rel": "app",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/5"
        },
        {
          "rel": "artifacts",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/5/artifacts"
        }
      ]
    },
    {
      "id": 7,
      "appOnBoardingAppId": 4,
      "healthStatus": "TERMINATED",
      "targetStatus": "TERMINATED",
      "createdTimestamp": "2022-10-13T13:18:21.148045Z[UTC]",
      "additionalParameters": "{}",
      "links": [
        {
          "rel": "self",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/7"
        },
        {
          "rel": "artifact-instances",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/7/artifact-instances"
        },
        {
          "rel": "app",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/4"
        },
        {
          "rel": "artifacts",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/4/artifacts"
        }
      ]
    },
    {
      "id": 13,
      "appOnBoardingAppId": 5,
      "healthStatus": "TERMINATED",
      "targetStatus": "TERMINATED",
      "createdTimestamp": "2022-10-25T10:59:47.325984Z[UTC]",
      "additionalParameters": "{}",
      "links": [
        {
          "rel": "self",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/13"
        },
        {
          "rel": "artifact-instances",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/13/artifact-instances"
        },
        {
          "rel": "app",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/5"
        },
        {
          "rel": "artifacts",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/5/artifacts"
        }
      ]
    },
    {
      "id": 9,
      "appOnBoardingAppId": 4,
      "healthStatus": "TERMINATED",
      "targetStatus": "TERMINATED",
      "createdTimestamp": "2022-10-20T11:06:22.264135Z[UTC]",
      "additionalParameters": "{}",
      "links": [
        {
          "rel": "self",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/9"
        },
        {
          "rel": "artifact-instances",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/9/artifact-instances"
        },
        {
          "rel": "app",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/4"
        },
        {
          "rel": "artifacts",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/4/artifacts"
        }
      ]
    },
    {
      "id": 12,
      "appOnBoardingAppId": 5,
      "healthStatus": "FAILED",
      "targetStatus": "INSTANTIATED",
      "createdTimestamp": "2022-10-25T10:58:17.922286Z[UTC]",
      "additionalParameters": "{}",
      "links": [
        {
          "rel": "self",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/12"
        },
        {
          "rel": "artifact-instances",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/12/artifact-instances"
        },
        {
          "rel": "app",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/5"
        },
        {
          "rel": "artifacts",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/5/artifacts"
        }
      ]
    },
    {
      "id": 19,
      "appOnBoardingAppId": 5,
      "healthStatus": "FAILED",
      "targetStatus": "INSTANTIATED",
      "createdTimestamp": "2022-10-25T12:49:18.400053Z[UTC]",
      "additionalParameters": "{}",
      "links": [
        {
          "rel": "self",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/19"
        },
        {
          "rel": "artifact-instances",
          "href": "http://eric-oss-app-lcm:8080/app-manager/lcm/app-lcm/v1/app-instances/19/artifact-instances"
        },
        {
          "rel": "app",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/5"
        },
        {
          "rel": "artifacts",
          "href": "http://eric-oss-app-lcm:8080/app-manager/onboarding/v1/apps/5/artifacts"
        }
      ]
    }
  ]
}
'''
