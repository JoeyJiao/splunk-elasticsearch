#!/usr/bin/env python
#
# Copyright 2011-2014 Splunk, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


# python essearch.py __EXECUTE__ 'q="New York"'

from datetime import datetime
from elasticsearch import Elasticsearch
import os, sys, time, requests, oauth2, json, urllib
#import splunk.Intersplunk

#(isgetinfo, sys.argv) = splunk.Intersplunk.isGetInfo(sys.argv)

from splunklib.searchcommands import \
  dispatch, GeneratingCommand, Configuration, Option, validators

@Configuration()
class EsCommand(GeneratingCommand):
  """ Generates events that are the result of a query against Elasticsearch

  ##Syntax

  .. code-block::
      es server=localhost func=<string> kwargs=[eval query="\"{
    'index'=<string>,
    'q'=<string>,
    'size'=<int>,
    'body'="{
    \"query\": {
           \"filtered\": {
               \"query\": {
                   \"query_string\": {
                       \"query\": \"*\"
                   }
               }
           }
       }
    }\""


  ##Description

  The :code:`es` issue a query to ElasticSearch, where the 
  query is specified in :code:`q`.

  ##Example

  .. code-block::
      | es body="{
    \"query\": {
           \"filtered\": {
               \"query\": {
                   \"query_string\": {
                       \"query\": \"*\"
                   }
               }
           }
       }
    }"
    

  This example generates events drawn from the result of the query 

  """
  server = Option(doc='', require=False, default="localhost")

  port = Option(doc='', require=False, default="9200")

  func = Option(doc='', require=False, default="search")

  kwargs = Option(doc='', require=True, default='{}')


  def generate(self):

    #self.logger.debug('SimulateCommand: %s' % self)  # log command line

    # config = self.get_configuration()
 
    #pp = pprint.PrettyPrinter(indent=4)
    self.logger.debug('Setup ES')
    es = Elasticsearch('{}:{}'.format(self.server, self.port))


    def get_func(es, func):
      array = func.split('.')
      object = getattr(es, array[0])
      if len(array) == 1:
        return object

      return get_func(object, '.'.join(array[1:]))


    #pp.pprint(body);
    res = get_func(es, self.func)(**json.loads(self.kwargs));

    # if response.status_code != 200:
    #   yield {'ERROR': results['error']['text']}
    #   return


    # date_time = '2014-12-21T16:11:18.419Z'
    # pattern = '%Y-%m-%dT%H:%M:%S.%fZ'

    yield self.getEvent(res)

  def getEvent(self, result):

    # hit["_source"][defaultField] = hit["_source"][defaultField].replace('"',' ');
    # epochTimestamp = hit['_source']['@timestamp'];
    # hit['_source']['_epoch'] = int(time.mktime(time.strptime(epochTimestamp, pattern)))
    # hit['_source']["_raw"]=hit['_source'][defaultField]

    event = {
        '_time': time.time(), 
        '_raw': result
    }

    return event

  def get_configuration(self):
    sourcePath = os.path.dirname(os.path.abspath(__file__))
    config_file = open(sourcePath + '/config.json')
    return json.load(config_file)

  def __init__(self):
    super(GeneratingCommand, self).__init__()

dispatch(EsCommand, sys.argv, sys.stdin, sys.stdout, __name__)
