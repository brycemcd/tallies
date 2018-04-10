# Tallies

> Sometimes it's useful to count things

## Boostrap

This project uses docker to bootstrap its environment. To spin up a dev environment, run `docker-compose up` from
the root directory.

## API documentation

POST /v1/tally/<tallyable>

Count some tallyable thing. Tallyable could be food, beer ... whatever

Success:

```json
{
"success" : true,
"tallyable" : "food",
"tallyable_cnt": 12,
"tallies": [
    "2018-03-16T02:48:45.458684", 
    "2018-03-16T02:47:04.337460", 
    "2018-03-16T02:46:35.571259", 
    "2018-03-16T02:46:34.091411", 
    "2018-03-16T02:46:27.664641", 
    "2018-03-16T02:08:57.834036", 
    "2018-03-16T02:03:40.405311", 
    "2018-03-16T02:03:38.608682", 
    "2018-03-16T02:02:12.374405", 
    "2018-03-16T02:02:11.089134"
  ] 
}
```

Fail:

```json
{"success": False}
```

Good luck figuring out why the response failed :P


## Alexa Handler

In skill_handlers, a module called tallies exists which represents the AWS
Lambda function that is called when Alexa wants to tally something. To deploy,
simply copy and paste the module into the lambda function editor.

TODO: make a _much_ better deployment paradigm for this.

The lambda function handles intents from the Alexa skill and pushes messages onto
an SQS queue. Another python script takes messages off that queue and stuff them
into a database.