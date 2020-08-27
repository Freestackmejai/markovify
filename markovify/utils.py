from .chain import Chain
from .text import Text


def get_model_dict(thing):
    if isinstance(thing, Chain):
        if thing.compiled:
            raise ValueError("Not implemented for compiled markovify.Chain")
        return thing.model, thing.model_reversed
    if isinstance(thing, Text):
        print("text instance")
        if thing.chain.compiled:
            raise ValueError("Not implemented for compiled markovify.Chain")
        return thing.chain.model, thing.chain.model_reversed
    if isinstance(thing, list):
        print("list instance")
        return dict(thing[0]), dict(thing[1])
    if isinstance(thing, dict):
        print("dict instance")
        return thing[0], thing[1]

    raise ValueError(
        "`models` should be instances of list, dict, markovify.Chain, or markovify.Text")


def combine(models, weights=None):
    if weights is None:
        weights = [1 for _ in range(len(models))]

    if len(models) != len(weights):
        raise ValueError("`models` and `weights` lengths must be equal.")

    model_dicts = list(map(get_model_dict, models))
    # thing.model, thing.model_reversed' and thing.model 2, thing.model_reversed 2

    models_list = [model_dicts[0][0], model_dicts[1][0]]
    models_reversed_list = [model_dicts[0][1], model_dicts[1][1]]

    # print(type(model_dicts[0]))
    # for md in model_dicts[0]:
    #     print(type(md))
    #     print(md.keys())
    #     print(len(list(md.keys())[0]))
    # print(len(model_dicts))

    state_sizes = [len(list(md.keys())[0])
                   for md in models_list]

    if len(set(state_sizes)) != 1:
        raise ValueError("All `models` must have the same state size.")

    if len(set(map(type, models))) != 1:
        raise ValueError("All `models` must be of the same type.")

    c = {}

    for m, w in zip(models_list, weights):
        for state, options in m.items():
            current = c.get(state, {})
            for subseq_k, subseq_v in options.items():
                subseq_prev = current.get(subseq_k, 0)
                current[subseq_k] = subseq_prev + (subseq_v * w)
            c[state] = current

    c_reversed = {}

    for m, w in zip(models_reversed_list, weights):
        for state, options in m.items():
            current = c_reversed.get(state, {})
            for subseq_k, subseq_v in options.items():
                subseq_prev = current.get(subseq_k, 0)
                current[subseq_k] = subseq_prev + (subseq_v * w)
            c_reversed[state] = current

    c_list =[c, c_reversed]
    print("----_______")
    print(c_list[1])
    ret_inst = models[0]

    if isinstance(ret_inst, Chain):
        return Chain.from_json(c_list)

    if isinstance(ret_inst, Text):
        if any(m.retain_original for m in models):
            combined_sentences = []
            for m in models:
                if m.retain_original:
                    combined_sentences += m.parsed_sentences
            return ret_inst.from_chain(c_list, parsed_sentences=combined_sentences)
        else:
            return ret_inst.from_chain(c_list)
    if isinstance(ret_inst, list):
        return list(c.items())
    if isinstance(ret_inst, dict):
        return c_reversed
