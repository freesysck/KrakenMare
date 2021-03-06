#!/bin/bash

# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
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
#
# -- license --

/tmp/wait-for --timeout=240 schemaregistry:8081 || exit 1
/tmp/wait-for --timeout=240 schemaregistry:8085 || exit 1

cd /tmp
for protocol in *.avdl
do
  java -jar avro-tools-1.9.1.jar idl2schemata $protocol
done

for schema in *.avsc
do
  namespace=`jq -r .namespace < $schema`
  # name=`jq -r .name < $schema | tr '[:upper:]' '[:lower:]'`
  name=`jq -r .name < $schema`
  topic=`echo $namespace.$name`
  if ! java -jar avro-cli-0.2.7.jar validate -s $schema > /dev/null 2>&1 ; then
    echo "$schema fails to validate. Not pushed to schema registry. See below" >&2
    java -jar avro-cli-0.2.7.jar validate -s $schema 
  else
    if ! http --ignore-stdin POST schemaregistry:8085/subjects/$topic/versions Accept:application/vnd.schemaregistry.v1+json schema=@/tmp/$schema ; then
      echo "$schema failed to push to schema registry" >&2
    fi
  fi
done

# We push the schema we will use for connection to elastic to <topic>-value naming.  This is needed for TopicNameStrategy per
# https://docs.confluent.io/current/schema-registry/serializer-formatter.html#limitations
# https://github.com/confluentinc/kafka-connect-elasticsearch/issues/59
http --ignore-stdin POST schemaregistry:8085/subjects/agent-registration-value/versions Accept:application/vnd.schemaregistry.v1+json schema=@/tmp/RegisterResponse.avsc
http --ignore-stdin POST schemaregistry:8085/subjects/device-registration-value/versions Accept:application/vnd.schemaregistry.v1+json schema=@/tmp/Agent.avsc
http --ignore-stdin POST schemaregistry:8085/subjects/agent-deregistration-value/versions Accept:application/vnd.schemaregistry.v1+json schema=@/tmp/DeregisterResponse.avsc
