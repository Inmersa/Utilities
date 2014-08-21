#!/usr/bin/python

import inmersa.scheduler

sch = inmersa.scheduler.Schedule('Inmersa-cron.ini')

sch.load()

sch.run()
