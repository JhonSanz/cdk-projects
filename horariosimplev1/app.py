#!/usr/bin/env python3

import aws_cdk as cdk

from horariosimplev1.horariosimplev1_stack import Horariosimplev1Stack


app = cdk.App()
Horariosimplev1Stack(app, "Horariosimplev1Stack")

app.synth()
