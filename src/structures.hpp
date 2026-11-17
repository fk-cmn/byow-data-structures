#pragma once
#include <algorithm>
#include <stdexcept>
#include <utility>
#include <vector>

namespace relic {
// 并查集：路径压缩 + 按集合大小合并。用于 Kruskal 判环。
class DisjointSet {
    std::vector<int> parent, size;
public:
    explicit DisjointSet(int n) : parent(n), size(n, 1) {
        for (int i = 0; i < n; ++i) parent[i] = i;
    }
    int find(int x) { return parent[x] == x ? x : parent[x] = find(parent[x]); }
    bool unite(int a, int b) {
        a = find(a); b = find(b);
        if (a == b) return false;
        if (size[a] < size[b]) std::swap(a, b);
        parent[b] = a; size[a] += size[b]; return true;
    }
};

// 顺序循环队列：预留一个空槽区分队满和队空，扩容时保持 FIFO 次序。
template <class T> class RingQueue {
    std::vector<T> data;
    size_t head = 0, tail = 0;
    void grow() {
        std::vector<T> next(data.size() * 2);
        size_t n = 0;
        while (!empty()) next[n++] = pop();
        data = std::move(next); head = 0; tail = n;
    }
public:
    explicit RingQueue(size_t capacity = 16) : data(std::max(size_t(2), capacity)) {}
    bool empty() const { return head == tail; }
    void push(const T& value) {
        if ((tail + 1) % data.size() == head) grow();
        data[tail] = value; tail = (tail + 1) % data.size();
    }
    T pop() {
        if (empty()) throw std::logic_error("empty queue");
        T value = data[head]; head = (head + 1) % data.size(); return value;
    }
};

// 自实现二叉最小堆。Compare(a,b) 为真表示 a 应先于 b 出队。
template <class T, class Compare> class MinHeap {
    std::vector<T> data;
    Compare before;
public:
    bool empty() const { return data.empty(); }
    void push(const T& value) {
        data.push_back(value);
        size_t i = data.size() - 1;
        while (i && before(data[i], data[(i - 1) / 2])) {
            std::swap(data[i], data[(i - 1) / 2]); i = (i - 1) / 2;
        }
    }
    T pop() {
        if (empty()) throw std::logic_error("empty heap");
        T result = data.front(); data.front() = data.back(); data.pop_back();
        size_t i = 0;
        while (2 * i + 1 < data.size()) {
            size_t j = 2 * i + 1;
            if (j + 1 < data.size() && before(data[j + 1], data[j])) ++j;
            if (!before(data[j], data[i])) break;
            std::swap(data[i], data[j]); i = j;
        }
        return result;
    }
};
}
