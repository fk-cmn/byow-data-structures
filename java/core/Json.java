package core;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** 仅用于读取本地 C++ 引擎输出；不依赖网络 JSON 服务或额外 jar。 */
public final class Json {
    private final String input;
    private int at;

    private Json(String input) { this.input = input; }

    public static Object parse(String text) {
        Json parser = new Json(text);
        Object value = parser.value();
        parser.space();
        if (parser.at != text.length()) throw new IllegalArgumentException("Trailing JSON data");
        return value;
    }

    private void space() {
        while (at < input.length() && Character.isWhitespace(input.charAt(at))) at++;
    }

    private char take() {
        if (at >= input.length()) throw new IllegalArgumentException("Incomplete JSON");
        return input.charAt(at++);
    }

    private Object value() {
        space();
        if (at >= input.length()) throw new IllegalArgumentException("Empty JSON");
        char c = input.charAt(at);
        if (c == '"') return string();
        if (c == '{') {
            at++;
            Map<String, Object> map = new LinkedHashMap<>();
            space();
            if (input.charAt(at) == '}') { at++; return map; }
            while (true) {
                space(); String key = string(); space();
                if (take() != ':') throw new IllegalArgumentException("Expected colon");
                map.put(key, value()); space(); char next = take();
                if (next == '}') return map;
                if (next != ',') throw new IllegalArgumentException("Expected comma");
            }
        }
        if (c == '[') {
            at++;
            List<Object> list = new ArrayList<>();
            space();
            if (input.charAt(at) == ']') { at++; return list; }
            while (true) {
                list.add(value()); space(); char next = take();
                if (next == ']') return list;
                if (next != ',') throw new IllegalArgumentException("Expected comma");
            }
        }
        for (String literal : new String[]{"true", "false", "null"}) {
            if (input.startsWith(literal, at)) {
                at += literal.length();
                return literal.equals("null") ? null : literal.equals("true");
            }
        }
        int begin = at;
        while (at < input.length() && "-+0123456789.eE".indexOf(input.charAt(at)) >= 0) at++;
        if (begin == at) throw new IllegalArgumentException("Invalid JSON value");
        return Double.valueOf(input.substring(begin, at));
    }

    private String string() {
        if (take() != '"') throw new IllegalArgumentException("Expected string");
        StringBuilder text = new StringBuilder();
        while (true) {
            char c = take();
            if (c == '"') return text.toString();
            if (c != '\\') { text.append(c); continue; }
            char escape = take();
            switch (escape) {
                case '"', '\\', '/' -> text.append(escape);
                case 'n' -> text.append('\n');
                case 'r' -> text.append('\r');
                case 't' -> text.append('\t');
                case 'b' -> text.append('\b');
                case 'f' -> text.append('\f');
                case 'u' -> {
                    text.append((char) Integer.parseInt(input.substring(at, at + 4), 16)); at += 4;
                }
                default -> throw new IllegalArgumentException("Invalid escape");
            }
        }
    }

    @SuppressWarnings("unchecked")
    public static Map<String, Object> object(Object value) { return (Map<String, Object>) value; }
    @SuppressWarnings("unchecked")
    public static List<Object> array(Object value) { return (List<Object>) value; }
    public static int number(Object value) { return ((Number) value).intValue(); }
}
