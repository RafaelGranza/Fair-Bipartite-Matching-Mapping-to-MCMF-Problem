import igraph as ig
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import random as rd

class quote:
    def __init__(self, characteristic, distribution, scale=True):
        self.characteristic = characteristic
        self.distribution = distribution
        total = sum([ x[1] for x in self.distribution ])
        if scale:
            map(lambda x: [x[0], x[1]/total] , self.distribution)
        elif total < 1:
            distribution.append(['Remaining', 1-total])

    def __str__(self):
        return "{ " + str(self.characteristic) + ": " + str(self.distribution) + " }"

    def __mul__(self, obj):
        if len(self.distribution) == 0:
            return obj 

        if len(obj.distribution) == 0:
            return self

        new_distribution = []
        for distribution_1 in self.distribution:
            for distribution_2 in obj.distribution:
                new_distribution.append([distribution_1[0] + '+' + distribution_2[0], distribution_1[1] * distribution_2[1]])
        return quote(self.characteristic + '/' + obj.characteristic, new_distribution)

class quotes_description:
    def __init__(self, quotes):
        self.requirement = self.combine_quotes(quotes)

    def __str__(self):
        return str(self.requirement)
    
    def characteristic(self):
        return self.requirement.characteristic

    def distribution(self):
        return self.requirement.distribution

    def combine_quotes(self, quotes):
        new_requirement = quote("", [])
        for requirement in quotes:
            new_requirement *= requirement
        return new_requirement
proxy={}
class mapper:
    def __init__(self, group_a, group_b, matches, quotes_group_a):
        self.group_a = group_a
        self.group_b = group_b
        self.matches = matches
        self.quotes_group_a = quotes_group_a
        self.number_of_matches = len(group_b)

        self.graph = self.build_graph()

    def build_graph(self):
        global proxy
        proxy={}
        g = ig.Graph(directed=True)
        G = nx.Graph()
        G.add_node(len(g.vs), subset=0, name="source", label='Source')
        g.add_vertex(type='source', name="source")

        
        remaining_matches = self.number_of_matches
        for group in self.quotes_group_a.requirement.distribution:
            G.add_node(len(g.vs), name=group[0], label='Fair Group', quotes=group[1], subset=1, obj=group)
            g.add_vertex(name=group[0], quotes=group[1], type='Fair Group', obj=group)
            G.add_edge(0, len(g.vs)-1, capacity=group[1], weight=0)
            g.add_edge(0, len(g.vs)-1, capacity=group[1], weight=0)
            remaining_matches-=group[1]

        # Remaining
        if len(self.quotes_group_a.requirement.distribution):
            G.add_node(len(g.vs), name="Remaining", label='Fair Group', subset=1, obj={'extra': True})
            g.add_vertex(name="Remaining", type='Fair Group', obj={'extra': True})
            G.add_edge(0, len(g.vs)-1, capacity=remaining_matches, weight=0)
            g.add_edge(0, len(g.vs)-1, capacity=remaining_matches, weight=0)

        for obj in self.group_a:
            G.add_node(len(g.vs), obj=obj, subset=3, name="Worker", label='Worker')
            g.add_vertex(obj=obj, type='group_a')

        self.add_edges_group_and_requirement(self.group_a, self.quotes_group_a, 0, g, G)


        for obj in self.group_b:
            G.add_node(len(g.vs), obj=obj, subset=4, name="Job", label='Job')
            g.add_vertex(obj=obj, type='group_b')

        
        for hash in self.matches:
            [[_, u], [_, v], [_, w]] = hash.items()
            G.add_edge(g.vs.find(obj=self.group_a[u]).index, g.vs.find(obj=self.group_b[v]).index, capacity=1, weight=w)
            g.add_edge(g.vs.find(obj=self.group_a[u]).index, g.vs.find(obj=self.group_b[v]).index, capacity=1, weight=w)

        G.add_node(len(g.vs), subset=6, name="target", label='Target')
        g.add_vertex(type='target', name="target")

        self.add_edges_group_and_requirement(self.group_b, quotes_description([]), len(g.vs)-1, g, G)
        

        return G

    def has_quotes(self, quotes):
        return len(quotes.requirement.distribution) >= 1

    def add_edges_group_and_requirement(self, group, requirement, in_case_its_empty, g, G):
        list_of_characteristics = requirement.requirement.characteristic.split('/')
        if len(requirement.requirement.distribution) == 0:
            for obj in group:
                g.add_edge(in_case_its_empty, g.vs.find(obj=obj).index, capacity=1, weight=0)
                G.add_edge(in_case_its_empty, g.vs.find(obj=obj).index, capacity=1, weight=0)

        else:

            
            list_proxy=[]
            for dist in requirement.requirement.distribution:
                list_of_distribution = dist[0].split('/')    
                for obj in group:
                    if not sum([obj[list_of_characteristics[i]] != list_of_distribution[i] for i in range(len(list_of_distribution))]):
                        if obj not in proxy.values():
                            key=rd.random()
                            G.add_node(len(g.vs), subset=2, obj=key, name="proxy", label='proxy')
                            g.add_vertex(name='proxy', type='proxy', obj=key)
                            g.add_edge(len(g.vs)-1, g.vs.find(obj=obj).index, capacity=1, weight=0, type='proxy')
                            G.add_edge(len(g.vs)-1, g.vs.find(obj=obj).index, capacity=1, weight=0, type='proxy')
                            proxy[key] = obj
                        g.add_edge(g.vs.find(obj=dist).index, len(g.vs)-1, capacity=1, weight=0)
                        G.add_edge(g.vs.find(obj=dist).index, len(g.vs)-1, capacity=1, weight=0)

                        

            
            for obj in group:
                if obj not in proxy.values():
                    key=rd.random()
                    G.add_node(len(g.vs), subset=2, obj=key, name="proxy", label='proxy')
                    g.add_vertex(name='proxy', type='proxy', obj=key)
                    g.add_edge(len(g.vs)-1, g.vs.find(obj=obj).index, capacity=1, weight=0, type='proxy')
                    G.add_edge(len(g.vs)-1, g.vs.find(obj=obj).index, capacity=1, weight=0, type='proxy')
                    proxy[key] = obj
                proxy_obj = [i for i in proxy if proxy[i]==obj][0]
                g.add_edge(g.vs.find(obj={'extra': True}).index, g.vs.find(obj=proxy_obj).index, capacity=1, weight=0)
                G.add_edge(g.vs.find(obj={'extra': True}).index, g.vs.find(obj=proxy_obj).index, capacity=1, weight=0)

def prepare_edge_labels(G, solved):
    if not solved:
        return {(u, v): (str(d["capacity"]) + ' - ' + str(d["weight"])) for u, v, d in G.edges(data=True)}
    else:
        return {(u, v): (str(d["used"]) + ' - ' + str(d["weight"])) for u, v, d in G.edges(data=True)}

def print_graph(G, solved=False, title="", flow=0, cost=0):
    fig, ax = plt.subplots(figsize=(15,9))
    color_by_type = [
            "cyan",
            "pink",
            "brown",
            "brown",
            "orange",
            "purple",
            "cyan"
    ]

    pos = nx.multipartite_layout(G)
    array_op = lambda arr, dx, dy: np.array([arr[0]*dx, arr[1]*dy])
    pos = {p:array_op(pos[p], 20, 5) for p in pos}
    for p in pos:
        obj = G.nodes[p].get('obj', None)
        if obj in proxy.values():
            proxy_obj = [i for i in proxy if proxy[i]==obj][0]
            proxy_pos = [id for [id, v] in G.nodes.items() if v.get('obj') == proxy_obj][0]
            pos[p] = np.array([pos[p][0], pos[proxy_pos][1]])


    color = [color_by_type[data["subset"]] for _, data in G.nodes(data=True)]
    node_options = {idx:'fill='+str(c)+', rounded corners'  for idx, c in enumerate(color)}
    nx.draw(G, pos, node_color=color, node_size=3000)
    
    node_label={
        'font_size': 10,
        'font_family': "sans-serif",
        'labels':{n: G.nodes[n]['name'] for n in G.nodes}
    }
    nx.draw_networkx_labels(G, pos, **node_label)

    alpha= [(('used' in G.edges[u, v]) and G.edges[u, v]['used']!= 0)*0.8 +0.2 for [u, v] in G.edges]
    edge_options= {(u, v): ('lightgray, text=black, font=\\footnotesize' if(not solved or 'used' in G.edges[u, v] and G.edges[u, v]['used']!= 0) else 'transparent') for [u, v] in G.edges}
    nx.draw_networkx_edges(
        G,
        pos,
        width=5,
        alpha= alpha
    )

    edge_labels = prepare_edge_labels(G, solved)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)   

    plt.title(title)
    ax.text(5, 3, r'Matches: ' + str(flow), fontsize = 15)
    ax.text(5, 3.5, r'Cost: ' + str(cost), fontsize = 15)
    plt.show()
    # breakpoint()
    # print(nx.to_latex_raw(G, pos, node_options=node_options, edge_options=edge_options, edge_label=edge_labels))
    
def update_graph(G, mincostFlow):
    for u in mincostFlow:
        for v in mincostFlow[u]:
            if u>v and G.edges[u, v].get('type') == 'proxy' and  G.edges[u, v]["used"]==0:
                 G.edges[u, v]["used"] = mincostFlow[u][v]
            if u > v: continue
            G.edges[u, v]["used"] = mincostFlow[u][v]

def solve(G):
    mincostFlow = nx.max_flow_min_cost(G, 0, len(G.nodes)-1)
    update_graph(G, mincostFlow)
    return[nx.maximum_flow_value(G, 0, len(G.nodes)-1), nx.cost_of_flow(G, mincostFlow)]


def gen_empty_nodes(qnt):
    list = []
    for i in range(qnt):
        list.append({"ID": i})
    return list

def gen_humans(qnt):
    list = []
    caracteristica = ["Negro - H", "Negro - M", "Pardo - M",  "Pardo - H",  "Branco - M",  "Branco - H"]
    
    for i in range(0, int(qnt*0.8)):
        list.append({
            "ID": i,
            "Caracteristica": caracteristica[5]
            })
    for i in range(int(qnt*0.8), qnt):
        list.append({
            "ID": i,
            "Caracteristica": caracteristica[rd.randint(0,len(caracteristica)-1)]
            })
    return list

def gen_matching(qnt_group_a, qnt_group_b, qnt_matches):
    list = []
    for _ in range(qnt_matches):
        source= rd.randint(0,qnt_group_a-1)
        list.append({
            "source": source,
            "destiny": rd.randint(0,qnt_group_b-1),
            'weight': rd.randint(1, 1) if source < 80 else 100000
            })
    return list
        

if __name__ == '__main__':
    # quotes = [quote("Raça", [["Branco", 0.5], ["Não Branco", 0.5]]), quote("Sexo", [["F", 0.5], [ "M", 0.5]]), quote("Origem", [["EU", 0.3], ["SA", 0.3], ["NA", 0.4]])]
    quotes = quotes_description([quote("Caracteristica", [["Negro - H", 1], ["Negro - M", 2], ["Pardo - M", 2], ["Pardo - H", 1], ["Branco - M", 1]])])
    qnt_a = 100
    qnt_b = 20
    a = gen_humans(qnt_a)
    b = gen_empty_nodes(qnt_b)
    matching = gen_matching(qnt_a, qnt_b, 1000)
    m = mapper(a, b, matching, quotes)
    # print_graph(m.graph, False, "Mapping with Fairness")
    [f, c] = solve(m.graph)
    print(f, c)
    # print_graph(m.graph, True, "Mapping with Fairness [SOLVED]", f, c)

    m = mapper(a, b, matching, quotes_description([]))
    # print_graph(m.graph, False,  "Mapping without Fairness")
    # breakpoint()
    [f, c] = solve(m.graph)
    print(f, c)
    # print_graph(m.graph, True,  "Mapping without Fairness [SOLVED]", f, c)