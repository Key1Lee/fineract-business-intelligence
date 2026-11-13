# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements. See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from email.message import Message

import pytest

from scripts.check_licenses import _declared_license


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("Apache-2.0", "SAFE"),
        ("MIT", "SAFE"),
        ("BSD-3-Clause", "SAFE"),
        ("GPL-3.0-only", "RESTRICTED"),
        ("MIT AND GPL-3.0-only", "UNKNOWN"),
        ("MIT OR GPL-3.0-only", "UNKNOWN"),
        ("GPL-2.0-only WITH Classpath-exception-2.0", "UNKNOWN"),
        ("LicenseRef-MIT-like", "UNKNOWN"),
    ],
)
def test_license_expression_takes_precedence(expression, expected):
    metadata = Message()
    metadata["License-Expression"] = expression
    metadata["License"] = "MIT"
    metadata["Classifier"] = "License :: OSI Approved :: MIT License"
    assert _declared_license(metadata) == (expression, expected)


def test_pre_pep639_metadata_uses_classifier_or_legacy_license():
    metadata = Message()
    assert _declared_license(metadata) == ("UNKNOWN", "UNKNOWN")
    metadata["License"] = "GPL"
    assert _declared_license(metadata) == ("GPL", "RESTRICTED")
    metadata["Classifier"] = "License :: OSI Approved :: BSD License"
    assert _declared_license(metadata) == ("BSD License", "SAFE")
