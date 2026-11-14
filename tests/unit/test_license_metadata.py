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
from types import SimpleNamespace

import pytest

from scripts import check_licenses


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("Apache-2.0", "SAFE"),
        ("MIT", "SAFE"),
        ("BSD-3-Clause", "SAFE"),
        ("GPL-3.0-only", "RESTRICTED"),
        ("AGPL-1.0-or-later", "RESTRICTED"),
        ("GPL-2.0", "RESTRICTED"),
        ("LGPL-2.1+", "RESTRICTED"),
        ("CC-BY-NC-ND-4.0", "RESTRICTED"),
        ("CC-BY-NC-SA-2.0-UK", "RESTRICTED"),
        ("CC-BY-SA-3.0", "RESTRICTED"),
        ("CDDL-1.1", "RESTRICTED"),
        ("CPL-1.0", "RESTRICTED"),
        ("OSL-3.0", "RESTRICTED"),
        ("EUPL-1.2", "RESTRICTED"),
        ("PolyForm-Noncommercial-1.0.0", "RESTRICTED"),
        ("copyleft-next-0.3.1", "RESTRICTED"),
        ("CC-BY-NC-99.0", "UNKNOWN"),
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
    assert check_licenses._declared_license(metadata) == (expression, expected)


def test_pre_pep639_metadata_uses_classifier_or_legacy_license():
    metadata = Message()
    assert check_licenses._declared_license(metadata) == ("UNKNOWN", "UNKNOWN")
    metadata["License"] = "GPL"
    assert check_licenses._declared_license(metadata) == ("GPL", "RESTRICTED")
    metadata["Classifier"] = "License :: OSI Approved :: BSD License"
    assert check_licenses._declared_license(metadata) == ("BSD License", "SAFE")


@pytest.mark.parametrize(
    ("expression", "classifier", "exit_code", "summary"),
    [
        ("CC-BY-NC-4.0", "License :: Free for non-commercial use", 1, "[FAIL] 1 Category X"),
        ("PSF-2.0", "License :: OSI Approved :: Python Software Foundation License", 0, "[PASS] 1 safe"),
    ],
)
def test_cli_exit_for_installed_direct_dependency(monkeypatch, capsys, expression, classifier, exit_code, summary):
    metadata = Message()
    metadata["Name"] = "example-package"
    metadata["Version"] = "1.0"
    metadata["License-Expression"] = expression
    metadata["Classifier"] = classifier
    monkeypatch.setattr(check_licenses, "_collect_direct_deps", lambda: {"example-package"})
    distributions = [SimpleNamespace(metadata=metadata)]
    monkeypatch.setattr(check_licenses.importlib.metadata, "distributions", lambda: distributions)

    assert check_licenses.main() == exit_code
    assert summary in capsys.readouterr().out
