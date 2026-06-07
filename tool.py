import cv2
import numpy as np
import json

class NodePathPlanner:
    def __init__(self, image_path):
        # 读取图片
        self.img = cv2.imread(image_path)
        if self.img is None:
            raise ValueError(f"无法读取图片: {image_path}")
        
        self.original_img = self.img.copy()
        self.nodes = []  #节点坐标
        self.node_labels = []  #节点标签
        self.edges = []  #边
        
        #鼠标交互
        self.current_state = "adding_nodes"
        self.start_node = None
        self.temp_points = []
        
        cv2.namedWindow("Path Planner")
        cv2.setMouseCallback("Path Planner", self.mouse_callback)
        
        #按钮
        self.button_height = 50
        self.add_node_btn = (10, self.img.shape[0] - self.button_height + 10, 120, 35)
        self.add_edge_btn = (140, self.img.shape[0] - self.button_height + 10, 120, 35)
        self.save_btn = (270, self.img.shape[0] - self.button_height + 10, 80, 35)
        self.clear_all_btn = (360, self.img.shape[0] - self.button_height + 10, 100, 35)
        
        self.running = True
        
    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if y > self.img.shape[0] - self.button_height:
                # 按钮点击处理
                if self.add_node_btn[0] <= x <= self.add_node_btn[0] + self.add_node_btn[2]:
                    self.current_state = "adding_nodes"
                    self.start_node = None
                    self.temp_points = []
                    print("切换到：添加节点模式")
                    return
                elif self.add_edge_btn[0] <= x <= self.add_edge_btn[0] + self.add_edge_btn[2]:
                    self.current_state = "adding_edges"
                    self.start_node = None
                    self.temp_points = []
                    print("切换到：添加边模式")
                    return
                elif self.save_btn[0] <= x <= self.save_btn[0] + self.save_btn[2]:
                    self.save_data()
                    return
                elif self.clear_all_btn[0] <= x <= self.clear_all_btn[0] + self.clear_all_btn[2]:
                    self.clear_all()
                    return
        
        if self.current_state == "adding_nodes" and event == cv2.EVENT_LBUTTONDOWN:
            if y < self.img.shape[0] - self.button_height:
                self.add_node(x, y)
        
        elif self.current_state == "adding_edges":
            if event == cv2.EVENT_LBUTTONDOWN:
                if y < self.img.shape[0] - self.button_height:
                    node_idx = self.find_nearest_node(x, y, threshold=15)
                    if node_idx is not None:
                        if self.start_node is None:
                            self.start_node = node_idx
                            self.temp_points = [self.nodes[node_idx]]
                            print(f"选择起始节点: {self.node_labels[node_idx]}")
                        else:
                            if node_idx != self.start_node:
                                self.finish_edge(node_idx)
                            else:
                                print("不能连接同一个节点")
                            self.start_node = None
                            self.temp_points = []
                    else:
                        if self.start_node is not None:
                            self.temp_points.append((x, y))
                            print(f"添加折线点: ({x}, {y})")
            
            elif event == cv2.EVENT_RBUTTONDOWN:
                if self.start_node is not None:
                    self.start_node = None
                    self.temp_points = []
                    print("取消当前边的绘制")
    
    def find_nearest_node(self, x, y, threshold=15):
        min_dist = threshold
        nearest = None
        for i, node in enumerate(self.nodes):
            dist = np.sqrt((node[0] - x)**2 + (node[1] - y)**2)
            if dist < min_dist:
                min_dist = dist
                nearest = i
        return nearest
    
    def add_node(self, x, y):
        node_idx = len(self.nodes)
        label = chr(ord('A') + node_idx) if node_idx < 26 else f"N{node_idx}"
        self.nodes.append((x, y))
        self.node_labels.append(label)
        print(f"添加节点 {label}: ({x}, {y})")
        self.update_display()
    
    def calculate_path_distance(self, points):
        total_dist = 0
        for i in range(len(points) - 1):
            dist = np.sqrt((points[i+1][0] - points[i][0])**2 + 
                          (points[i+1][1] - points[i][1])**2)
            total_dist += dist
        return total_dist
    
    def finish_edge(self, end_node):
        full_path = [self.nodes[self.start_node]] + self.temp_points[1:] + [self.nodes[end_node]]
        distance = self.calculate_path_distance(full_path)
        
        self.edges.append({
            'start': self.start_node,
            'end': end_node,
            'distance': distance,
            'path': full_path
        })
        
        print(f"添加边: {self.node_labels[self.start_node]} -> {self.node_labels[end_node]}, "
              f"距离: {distance:.2f} 像素, 折线点数: {len(full_path)}")
        self.update_display()
    
    def draw_ui_buttons(self, img):
        overlay = img.copy()
        cv2.rectangle(overlay, (0, img.shape[0] - self.button_height), 
                     (img.shape[1], img.shape[0]), (200, 200, 200), -1)
        img = cv2.addWeighted(overlay, 0.3, img, 0.7, 0)
        
        btn_color = (255, 255, 255)
        btn_bg = (100, 100, 100)
        
        color = (0, 200, 0) if self.current_state == "adding_nodes" else btn_bg
        cv2.rectangle(img, (self.add_node_btn[0], self.add_node_btn[1]),
                     (self.add_node_btn[0]+self.add_node_btn[2], self.add_node_btn[1]+self.add_node_btn[3]),
                     color, -1)
        cv2.putText(img, "Add Node", (self.add_node_btn[0]+10, self.add_node_btn[1]+25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, btn_color, 2)
        
        color = (0, 200, 0) if self.current_state == "adding_edges" else btn_bg
        cv2.rectangle(img, (self.add_edge_btn[0], self.add_edge_btn[1]),
                     (self.add_edge_btn[0]+self.add_edge_btn[2], self.add_edge_btn[1]+self.add_edge_btn[3]),
                     color, -1)
        cv2.putText(img, "Add Edge", (self.add_edge_btn[0]+10, self.add_edge_btn[1]+25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, btn_color, 2)
        
        # 保存按钮
        cv2.rectangle(img, (self.save_btn[0], self.save_btn[1]),
                     (self.save_btn[0]+self.save_btn[2], self.save_btn[1]+self.save_btn[3]),
                     (0, 100, 200), -1)
        cv2.putText(img, "Save", (self.save_btn[0]+10, self.save_btn[1]+25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, btn_color, 2)
        
        # 清空按钮
        cv2.rectangle(img, (self.clear_all_btn[0], self.clear_all_btn[1]),
                     (self.clear_all_btn[0]+self.clear_all_btn[2], self.clear_all_btn[1]+self.clear_all_btn[3]),
                     (0, 0, 200), -1)
        cv2.putText(img, "Clear All", (self.clear_all_btn[0]+10, self.clear_all_btn[1]+25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, btn_color, 2)
        
        return img
    
    def update_display(self):
        img = self.original_img.copy()
        
        for edge in self.edges:
            points = np.array(edge['path'], dtype=np.int32)
            cv2.polylines(img, [points], False, (0, 255, 0), 2)
            
            # 绘制折线点
            for point in edge['path'][1:-1]:
                cv2.circle(img, point, 3, (0, 255, 255), -1)
            
            #显示距离标签
            mid_idx = len(points) // 2
            cv2.putText(img, f"{edge['distance']:.1f}", 
                       (points[mid_idx][0]+5, points[mid_idx][1]-5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
        #绘制临时折线
        if self.start_node is not None and len(self.temp_points) > 1:
            points = np.array(self.temp_points, dtype=np.int32)
            cv2.polylines(img, [points], False, (0, 255, 255), 2)
        
        #绘制节点
        for i, (x, y) in enumerate(self.nodes):
            cv2.circle(img, (x, y), 8, (0, 0, 255), -1)
            cv2.circle(img, (x, y), 8, (255, 255, 255), 2)
            cv2.putText(img, self.node_labels[i], (x+10, y-5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        #显示状态
        status_text = f"Mode: {'Nodes' if self.current_state == 'adding_nodes' else 'Edges'}"
        if self.start_node is not None:
            status_text += f" | Selected: {self.node_labels[self.start_node]}"
        cv2.putText(img, status_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        img = self.draw_ui_buttons(img)
        cv2.imshow("Path Planner", img)
    
    def save_data(self):
        if len(self.nodes) == 0:
            print("没有节点数据可保存")
            return
        
        graph_json = {
            "image": "map.jpg",
            "nodes": [],
            "edges": []
        }
        
        for i, (x, y) in enumerate(self.nodes):
            graph_json["nodes"].append({
                "id": i,
                "label": self.node_labels[i],
                "x": x,
                "y": y
            })
        
        for edge in self.edges:
            path_list = [[p[0], p[1]] for p in edge['path']]
            
            graph_json["edges"].append({
                "from": edge['start'],
                "to": edge['end'],
                "distance": round(edge['distance'], 2),
                "path": path_list
            })
        
        with open('graph_data.json', 'w', encoding='utf-8') as f:
            json.dump(graph_json, f, indent=2, ensure_ascii=False)
        
        print(f"\n数据保存成功！")
        print(f"节点数: {len(self.nodes)}")
        print(f"边数: {len(self.edges)}")
    
    def clear_all(self):
        self.nodes = []
        self.node_labels = []
        self.edges = []
        self.current_state = "adding_nodes"
        self.start_node = None
        self.temp_points = []
        self.update_display()
        print("已清空所有数据")
    
    def run(self):
        self.update_display()
        
        while self.running:
            key = cv2.waitKey(100) & 0xFF
            if key == ord('q') or key == 27:
                break
            elif key == ord('n'):
                self.current_state = "adding_nodes"
                self.start_node = None
                self.temp_points = []
                print("切换到：添加节点模式")
                self.update_display()
            elif key == ord('e'):
                self.current_state = "adding_edges"
                self.start_node = None
                self.temp_points = []
                print("切换到：添加边模式")
                self.update_display()
            elif key == ord('s'):
                self.save_data()
            elif key == ord('c'):
                self.clear_all()
        
        cv2.destroyAllWindows()


def visualize_path(graph_json_path, path_edges):
    """
    graph_json_path: JSON文件路径
    path_edges: 最短路径经过的边列表，每个元素是(from, to)
    """
    import json
    import cv2
    import numpy as np
    
    with open(graph_json_path, 'r') as f:
        data = json.load(f)
    
    #读取地图
    img = cv2.imread(data['image'])
    
    #绘制所有边（默认设置为灰色）
    for edge in data['edges']:
        points = np.array(edge['path'], dtype=np.int32)
        cv2.polylines(img, [points], False, (128, 128, 128), 2)
    
    # 绘制最短路径（用红色加粗）
    for from_id, to_id in path_edges:
        for edge in data['edges']:
            if (edge['from'] == from_id and edge['to'] == to_id) or \
               (edge['from'] == to_id and edge['to'] == from_id):
                points = np.array(edge['path'], dtype=np.int32)
                cv2.polylines(img, [points], False, (0, 0, 255), 4)
                break
    
    # 绘制节点
    for node in data['nodes']:
        cv2.circle(img, (node['x'], node['y']), 8, (0, 0, 255), -1)
        cv2.circle(img, (node['x'], node['y']), 8, (255, 255, 255), 2)
        cv2.putText(img, node['label'], (node['x']+10, node['y']-5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    
    cv2.imshow("Shortest Path", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    planner = NodePathPlanner("map.jpg")
    planner.run()