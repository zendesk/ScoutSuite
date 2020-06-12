from ScoutSuite.core.console import print_debug, print_exception
from ScoutSuite.utils import manage_dictionary

from ScoutSuite.core.utils import recurse


class ProcessingEngine(object):
    """

    """

    def __init__(self, ruleset):
        # Organize rules by path
        self.ruleset = ruleset
        self.rules = {}
        for filename in self.ruleset.rules:
            for rule in self.ruleset.rules[filename]:
                if not rule.enabled:
                    continue
                try:
                    manage_dictionary(self.rules, rule.path, [])
                    self.rules[rule.path].append(rule)
                except Exception as e:
                    print_exception('Failed to create rule %s: %s' % (rule.filename, e))

    def run(self, cloud_provider, skip_dashboard=False):
        # Clean up existing findings
        for service in cloud_provider.services:
            cloud_provider.services[service][self.ruleset.rule_type] = {}

        # Process each rule
        for finding_path in self._filter_rules(self.rules, cloud_provider.service_list):
            for rule in self.rules[finding_path]:

                if not rule.enabled:  # or rule.service not in []: # TODO: handle this...
                    continue

                print_debug('Processing %s rule "%s" (%s)' % (rule.service, rule.description, rule.filename))
                finding_path = rule.path
                path = finding_path.split('.')
                service = path[0]
                manage_dictionary(cloud_provider.services[service], self.ruleset.rule_type, {})

                rule_dict = {"description": rule.description, "path": rule.path}
                for attr in ['level', 'id_suffix', 'class_suffix', 'display_path']:
                    if hasattr(rule, attr):
                        rule_dict[attr] = getattr(rule, attr)
                try:
                    setattr(rule, 'checked_items', 0)
                    rule_dict['items'] = recurse(cloud_provider.services, cloud_provider.services, path, [], rule, True)
                    if skip_dashboard:
                        continue
                    rule_dict["dashboard_name"] = rule.dashboard_name
                    rule_dict['checked_items'] = rule.checked_items
                    rule_dict['flagged_items'] = len(cloud_provider.services[service][self.ruleset.rule_type][rule.key]['items'])
                    rule_dict['service'] = rule.service
                    rule_dict['rationale'] = rule.rationale if hasattr(rule, 'rationale') else None
                    rule_dict['remediation'] = rule.remediation if hasattr(rule, 'remediation') else None
                    rule_dict['compliance'] = rule.compliance if hasattr(rule, 'compliance') else None
                    rule_dict['references'] = rule.references if hasattr(rule, 'references') else None
                    rule_dict['args'] = rule.args if hasattr(rule, "args") else None
                    rule_dict['conditions'] = rule.conditions if hasattr(rule, "conditions") else None
                except Exception as e:
                    print_exception('Failed to process rule defined in %s: %s' % (rule.filename, e))
                    # Fallback if process rule failed to ensure report creation and data dump still happen
                    rule_dict['checked_items'] = 0
                    rule_dict['flagged_items'] = 0

                cloud_provider.services[service][self.ruleset.rule_type][rule.key] = rule_dict

    @staticmethod
    def _filter_rules(rules, services):
        return {rule_name: rule for rule_name, rule in rules.items() if rule_name.split('.')[0] in services}
