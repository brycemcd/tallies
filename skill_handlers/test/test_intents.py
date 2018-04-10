import pytest
import json
import skill_handlers.tallies as skill

class TestIntents():
    """Test the basic workflow of an intent"""

    tally_one_beer_json = json.loads("""
    {
    "version": "1.0",
    "session": {
        "new": false,
        "sessionId": "amzn1.echo-api.session.178d618e-3c3e-4a74-9b2d-d14897f0a623",
        "application": {
            "applicationId": "amzn1.ask.skill.8f82b7d6-7bb7-4b72-9512-3e1d32f2f716"
        },
        "user": {
            "userId": "amzn1.ask.account.AFRJ4XTCFMQJZPS4SUEESPA3PTC7PJE33AGENTY4C7BKEEVEV6DSKAMTKEXB6YM3SOKKWBWSCNXLFNM2DPJ7K6UA7UQQNGJV3TGIWKNZSSM5BW2WSEHVRBGLBSSS4G2TQ3XLQ63AFI5LKN5NHE7UECVN5PZJSEECFCJETYKJPGXD2SXXMC7Z7OHECDNBA62ZCEQD7JNHP54W5WI"
        }
    },
    "context": {
        "AudioPlayer": {
            "playerActivity": "IDLE"
        },
        "Display": {
            "token": ""
        },
        "System": {
            "application": {
                "applicationId": "amzn1.ask.skill.8f82b7d6-7bb7-4b72-9512-3e1d32f2f716"
            },
            "user": {
                "userId": "amzn1.ask.account.AFRJ4XTCFMQJZPS4SUEESPA3PTC7PJE33AGENTY4C7BKEEVEV6DSKAMTKEXB6YM3SOKKWBWSCNXLFNM2DPJ7K6UA7UQQNGJV3TGIWKNZSSM5BW2WSEHVRBGLBSSS4G2TQ3XLQ63AFI5LKN5NHE7UECVN5PZJSEECFCJETYKJPGXD2SXXMC7Z7OHECDNBA62ZCEQD7JNHP54W5WI"
            },
            "device": {
                "deviceId": "amzn1.ask.device.AE4ATSYNNSBY65EFVZ5AY76NEA7O2ROA2WDZAQ7OMXB7NSDYKCZE2HAOMIP6SPF4KZTT444PRHNIVSATOWHXZC52XVJ234D34U2DQTCIVW7X3JAG6BE3PHA4BU6UTTSQ7ZLAX4CNKHM4MEMI45IKAIBHCA6Q",
                "supportedInterfaces": {
                    "AudioPlayer": {},
                    "Display": {
                        "templateVersion": "1.0",
                        "markupVersion": "1.0"
                    }
                }
            },
            "apiEndpoint": "https://api.amazonalexa.com",
            "apiAccessToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJhdWQiOiJodHRwczovL2FwaS5hbWF6b25hbGV4YS5jb20iLCJpc3MiOiJBbGV4YVNraWxsS2l0Iiwic3ViIjoiYW16bjEuYXNrLnNraWxsLjhmODJiN2Q2LTdiYjctNGI3Mi05NTEyLTNlMWQzMmYyZjcxNiIsImV4cCI6MTUyMzIxNTI1NCwiaWF0IjoxNTIzMjExNjU0LCJuYmYiOjE1MjMyMTE2NTQsInByaXZhdGVDbGFpbXMiOnsiY29uc2VudFRva2VuIjpudWxsLCJkZXZpY2VJZCI6ImFtem4xLmFzay5kZXZpY2UuQUU0QVRTWU5OU0JZNjVFRlZaNUFZNzZORUE3TzJST0EyV0RaQVE3T01YQjdOU0RZS0NaRTJIQU9NSVA2U1BGNEtaVFQ0NDRQUkhOSVZTQVRPV0hYWkM1MlhWSjIzNEQzNFUyRFFUQ0lWVzdYM0pBRzZCRTNQSEE0QlU2VVRUU1E3WkxBWDRDTktITTRNRU1JNDVJS0FJQkhDQTZRIiwidXNlcklkIjoiYW16bjEuYXNrLmFjY291bnQuQUZSSjRYVENGTVFKWlBTNFNVRUVTUEEzUFRDN1BKRTMzQUdFTlRZNEM3QktFRVZFVjZEU0tBTVRLRVhCNllNM1NPS0tXQldTQ05YTEZOTTJEUEo3SzZVQTdVUVFOR0pWM1RHSVdLTlpTU001QlcyV1NFSFZSQkdMQlNTUzRHMlRRM1hMUTYzQUZJNUxLTjVOSEU3VUVDVk41UFpKU0VFQ0ZDSkVUWUtKUEdYRDJTWFhNQzdaN09IRUNETkJBNjJaQ0VRRDdKTkhQNTRXNVdJIn19.Rg1r0qLoSkajVRA1IP0xEqyJdMe8p1uxAPVajSV_b8FRLuvxDXVKAoHCSp0LMMonUKS584TXLiULIVcL3yliBLEgqFAclTO1jHc_nA8wqNgO1HUWgxnrP0mVpbGXS4i4txIOqvC7w1TA0e99AWzH3DJlNH1WZXDhHeY8zyPnd84oDWM6t25eF2GqbfsBvH-cORNWqIDbRlkTUtAMJyIKB2LonZugmFBKAsS63yAyy__aFd7I5DMQj073aOXbJvdqfbK2GMnABnzkoB8vzRrwugNVarPvPMyr3HPkmsZpD7WGZ4ZUQrEG0d8MhafNTZewSOXwl3D6d6n4Fv2shLeMBQ"
        }
    },
    "request": {
        "type": "IntentRequest",
        "requestId": "amzn1.echo-api.request.310d9d56-6af0-4e98-9a50-9fd1eb93e4d5",
        "timestamp": "2018-04-08T18:20:54Z",
        "locale": "en-US",
        "intent": {
            "name": "tally",
            "confirmationStatus": "NONE"
        },
        "dialogState": "STARTED"
    }
}""")

    def test_tally_one_beer(self):
        """Tests tallying one beer"""

        response = skill.get_welcome_response()
        assert len(response.keys()) == 3
