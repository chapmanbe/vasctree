import networkx as nx

crds = iu.get_crds(nodes,data['imgShape'])
crds = biu.get_crds(nodes,data['imgShape'])





crds[2].min()
crds[1].max()
posxy = array([crds[2],crds[1]])
pos
pos.shape
nx.draw_networkx_nodes(g,pos)
posc = nx.circular_layout(g)
posc.shape
posc
#?nx.layout
#?zip
tmp = zip(crds[0],crds[1])
tmp
#?dict
#?map
tmp2 = zip(nodes,tmp)
tmp2.keys()
tmp2[0]
pos = dict(tmp2)
pos.keys()
pos.values()
nx.draw_networkx_nodes(g,pos)
figure(2)
nx.draw_networkx_nodes(g,pos)
p1 = nx.draw_networkx_nodes(g,pos)
p1.show()
type(p1)
_ip.magic("history ")