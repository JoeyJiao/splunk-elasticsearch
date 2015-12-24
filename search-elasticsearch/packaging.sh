#!/bin/bash

app=$(basename $(pwd))
tar czv --exclude=.git --exclude=local ../${app} > ../${app}.tar.gz
mv ../${app}.tar.gz ../${app}.spl
