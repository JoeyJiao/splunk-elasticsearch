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
      esquery server=<string> func=<string> filter=<string> kwargs="{
    \"index\":<string>,
    \"size\":<int>,
    \"format\":\"json\"
    }"


  ##Description

  The :code:`esquery` issue a query to ElasticSearch, where the 
  filter specifies the key to filter out in dict,
  and kwargs specifies the keywords in es query function like index, size, body etc.

  ##Example

  .. code-block::
      | esquery server=hostname func="search" filter="hits.hits" kwargs="{
    \"index\": \"logstash\"
    }"
    
  .. code-block::
      | esquery server=hostname func="cat.indices" kwargs="{
    \"h\": \"index\",
    \"format\": \"json\"
    }"

  This example generates events drawn from the result of the query 

  """
  server = Option(doc='', require=False, default="localhost")

  port = Option(doc='', require=False, default="9200")

  func = Option(doc='', require=False, default="search")

  kwargs = Option(doc='', require=False, default='{}')

  filter = Option(doc='', require=False, default=None)


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

    def filter_field(res, field):
      array = field.split('.')
      result = res.get(array[0])
      if len(array) == 1:
        return result

      return filter_field(result, '.'.join(array[1:]))
        

    if type(res) == list:
      for hit in res:
        yield self.getEvent(hit)
    elif type(res) == dict:
      if not self.filter:
        yield self.getEvent(res)
      else:
        result = filter_field(res, self.filter)
        for hit in result:
          yield self.getEvent(hit)
    elif type(res) == unicode:
      for hit in res.split('\n'):
        yield self.getEvent(hit)
    else:
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
