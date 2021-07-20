#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# MODIFY:[6] line

from project import init_app

app = init_app()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
