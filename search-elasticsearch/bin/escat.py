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
      escat func=<string>


  ##Description

  The :code:`escat` issue a query to ElasticSearch, where the 
  function is specified in :code:`func`.

  ##Example

  .. code-block::
      | escat func="indices"


  This example generates events drawn from the result of the query 

  """
  server = Option(doc='', require=False, default="localhost")

  port = Option(doc='', require=False, default="9200")

  func = Option(doc='', require=False, default="indices")

  kwargs = Option(doc='', require=False, default="{}")

  def generate(self):

    #self.logger.debug('SimulateCommand: %s' % self)  # log command line

    config = self.get_configuration()
 
    #pp = pprint.PrettyPrinter(indent=4)
    self.logger.debug('Setup ES')
    es = Elasticsearch('{}:{}'.format(self.server, self.port))

    #pp.pprint(body);
    self.logger.debug('kwargs=' + self.kwargs)
    res = getattr(es.cat, self.func)(**json.loads(self.kwargs));

    # if response.status_code != 200:
    #   yield {'ERROR': results['error']['text']}
    #   return


    # date_time = '2014-12-21T16:11:18.419Z'
    # pattern = '%Y-%m-%dT%H:%M:%S.%fZ'

    for line in res.split('\n')[:-1]:
        yield self.getEvent(line)

  def getEvent(self, result):

    event = {'_time': time.time(), 
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
