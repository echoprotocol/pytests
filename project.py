# -*- coding: utf-8 -*-
import os.path
import sys

from lemoncheesecake.project import SimpleProjectConfiguration

project_dir = os.path.dirname(__file__)
sys.path.append(project_dir)

project = SimpleProjectConfiguration(
    suites_dir=os.path.join(project_dir, "suites"),
    fixtures_dir=os.path.join(project_dir, "fixtures"),
    report_title="Try to make awesome tests"
)
