from src.feature_extraction.database_loader import *
from src.feature_extraction.plan_features import *
from src.feature_extraction.sample_bitmap import *


def add_sample_bitmap(input_path, output_path, sample_num, data, sample):
    with open(input_path, 'r') as ff:
        with open(output_path, 'w') as f:
            for count, plan in enumerate(ff.readlines()):
                print(count)
                parsed_plan = json.loads(plan)
                nodes_with_sample = []
                for node in parsed_plan['seq']:
                    bitmap_filter = []
                    bitmap_index = []
                    bitmap_other = []
                    if node is not None and node.has_key('condition'):
                        predicates = node['condition']
                        if len(predicates) > 0:
                            root = TreeNode(predicates[0], None)
                            if len(predicates) > 1:
                                recover_tree(predicates[1:], root)
                            bitmap_other = get_bitmap(root, data, sample, sample_num)
                    if node is not None and node.has_key('condition_filter'):
                        predicates = node['condition_filter']
                        if len(predicates) > 0:
                            root = TreeNode(predicates[0], None)
                            if len(predicates) > 1:
                                recover_tree(predicates[1:], root)
                            bitmap_filter = get_bitmap(root, data, sample, sample_num)
                    if node is not None and node.has_key('condition_index'):
                        predicates = node['condition_index']
                        if len(predicates) > 0:
                            root = TreeNode(predicates[0], None)
                            if len(predicates) > 1:
                                recover_tree(predicates[1:], root)
                            bitmap_index = get_bitmap(root, data, sample, sample_num)
                    if len(bitmap_filter) > 0 or len(bitmap_index) > 0 or len(bitmap_other) > 0:
                        bitmap = [1 for _ in range(sample_num)]
                        bitmap = bitand(bitmap, bitmap_filter)
                        bitmap = bitand(bitmap, bitmap_index)
                        bitmap = bitand(bitmap, bitmap_other)
                        node['bitmap'] = ''.join([str(x) for x in bitmap])
                    nodes_with_sample.append(node)
                parsed_plan['seq'] = nodes_with_sample
                f.write(json.dumps(parsed_plan))
                f.write('\n')


def get_subplan(root):
    results = []
    if root.has_key('Actual Rows') and root.has_key('Actual Total Time') and root['Actual Rows'] > 0:
        results.append((root, root['Actual Total Time'], root['Actual Rows']))
    if root.has_key('Plans'):
        for plan in root['Plans']:
            results += get_subplan(plan)
    return results


def get_plan(root):
    return root, root['Actual Total Time'], root['Actual Rows']


class PlanInSeq(object):
    def __init__(self, seq, cost, cardinality):
        self.seq = seq
        self.cost = cost
        self.cardinality = cardinality


def get_alias2table(root, alias2table):
    if root.has_key('Relation Name') and root.has_key('Alias'):
        alias2table[root['Alias']] = root['Relation Name']
    if root.has_key('Plans'):
        for child in root['Plans']:
            get_alias2table(child, alias2table)


def feature_extractor(input_path, out_path):
    with open(out_path, 'w') as out:
        with open(input_path, 'r') as f:
            for index, plan in enumerate(f.readlines()):
                print(index)
                if plan != 'null\n':
                    plan = json.loads(plan)['Plan']
                    alias2table = {}
                    get_alias2table(plan, alias2table)
                    subplan, cost, cardinality = get_plan(plan)
                    seq, _ = plan2seq(subplan, alias2table)
                    seqs = PlanInSeq(seq, cost, cardinality)
                    out.write(class2json(seqs) + '\n')


def plan2seq(sample_num, database_path, plans_file_path, seq_output_path, seq_sample_output_path):
    data = load_dataset(database_path)
    sample = prepare_samples(data, sample_num)
    feature_extractor(plans_file_path, seq_output_path)
    add_sample_bitmap(seq_output_path, seq_sample_output_path, sample_num, data, sample)
