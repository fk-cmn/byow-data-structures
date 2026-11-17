package core;

import edu.princeton.cs.algs4.StdDraw;
import tileengine.TERenderer;
import tileengine.TETile;
import tileengine.Tileset;

import java.awt.Color;
import java.awt.Font;
import java.awt.event.KeyEvent;
import java.io.IOException;
import java.nio.file.Path;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * CS61B 原版 TileEngine 桌面入口。
 * 菜单按官方 3B 示例实现；砖块直接使用官方 Tileset，不另作网页或侧栏。
 * 此类只做输入/显示/调用本地引擎，图算法均在 C++ 源文件中。
 */
public final class Main {
    private static final int W = 57, H = 35, SCREEN_H = H + 5, OFFSET_Y = 2;
    private static final Font TITLE = new Font("Monaco", Font.BOLD, 30);
    private static final Font MENU_FONT = new Font("Monaco", Font.BOLD, 20);
    private static final Font HUD = new Font("Monospaced", Font.PLAIN, 12);
    private static final Font SMALL = new Font("Monospaced", Font.PLAIN, 11);
    // 附加玩法仍通过 TETile 表达，基础砖块、配色和字号保持官方原样。
    private static final TETile GUARD = new TETile('g', Color.RED, Color.BLACK, "guard", 20);
    private static final TETile HEAL = new TETile('+', Color.RED, Color.BLACK, "health +30", 21);
    private final TERenderer renderer = new TERenderer();
    private final EngineBridge engine;
    private String screen = "menu", returnScreen = "menu", seedText = "", notice = "";
    private long seed = 2026;
    private String history = "", replayHistory = "";
    private Map<String, Object> state;
    private TETile[][] tiles;
    private int target = -1, algorithm = 2, slot = 1, animationCount = Integer.MAX_VALUE;
    private boolean fog, enemyPaths, path = true, footprints, graph, walking, colon, replay;
    private boolean dirty = true, wasMouse;
    private long lastStep, lastAnimation;
    private int hovered = -2;
    private final Set<Integer> downKeys = new HashSet<>();

    private Main(Path root) { engine = new EngineBridge(root); }

    public static void main(String[] args) {
        new Main(Path.of(System.getProperty("byow.root", ".")).toAbsolutePath()).run();
    }

    private int number(String key) { return Json.number(state.get(key)); }
    private List<Object> list(String key) { return Json.array(state.get(key)); }
    private List<Integer> ints(Object array) { return Json.array(array).stream().map(Json::number).toList(); }
    private List<Integer> ints(String key) { return ints(state.get(key)); }
    private Map<String, Object> search(int index) {
        List<Object> searches = list("searches");
        return searches.isEmpty() ? null : Json.object(searches.get(index));
    }

    private void run() {
        renderer.initialize(W, SCREEN_H, 0, OFFSET_Y);
        StdDraw.setTitle("CS 61B: The Game");
        while (true) {
            try {
                while (StdDraw.hasNextKeyTyped()) key(Character.toLowerCase(StdDraw.nextKeyTyped()));
                arrowKeys();
                boolean pressed = StdDraw.isMousePressed();
                if (pressed && !wasMouse) mouse();
                wasMouse = pressed;
                if (screen.equals("world")) {
                    int current = mouseCell();
                    if (current != hovered) { hovered = current; dirty = true; }
                    long now = System.currentTimeMillis();
                    if ((walking || replay) && now - lastStep > 120) { lastStep = now; step(); }
                    if (animationCount != Integer.MAX_VALUE && now - lastAnimation > 30) {
                        animationCount += 6; lastAnimation = now; dirty = true;
                        Map<String, Object> route = search(algorithm);
                        if (route == null || animationCount >= Json.array(route.get("order")).size()) {
                            animationCount = Integer.MAX_VALUE;
                        }
                    }
                }
                if (dirty) { render(); dirty = false; }
            } catch (Exception error) {
                walking = replay = false; notice = "Error: " + error.getMessage(); dirty = true;
                error.printStackTrace();
            }
            StdDraw.pause(15);
        }
    }

    private void arrowKeys() throws IOException {
        int[] keys = {KeyEvent.VK_UP, KeyEvent.VK_LEFT, KeyEvent.VK_DOWN, KeyEvent.VK_RIGHT};
        char[] moves = {'w', 'a', 's', 'd'};
        for (int i = 0; i < keys.length; i++) {
            boolean held = StdDraw.isKeyPressed(keys[i]);
            if (held && downKeys.add(keys[i]) && screen.equals("world")) key(moves[i]);
            if (!held) downKeys.remove(keys[i]);
        }
    }

    private void refresh() throws IOException {
        state = engine.state(seed, history, target); rebuildTiles(); dirty = true;
    }

    private void start() throws IOException {
        long next = Long.parseLong(seedText);
        EngineBridge.validate(next, "");
        Map<String, Object> nextState = engine.state(next, "", -1);
        seed = next; history = ""; target = -1; state = nextState;
        screen = "world"; replay = walking = colon = false; notice = "";
        rebuildTiles(); dirty = true;
    }

    private void newSeed() {
        returnScreen = state == null ? "menu" : "world";
        screen = "seed"; seedText = ""; notice = ""; walking = replay = false; dirty = true;
    }

    private void load(int which, boolean playReplay) throws IOException {
        EngineBridge.Saved saved = engine.load(which);
        Map<String, Object> loaded = engine.state(saved.seed(), playReplay ? "" : saved.history(), -1);
        seed = saved.seed(); history = playReplay ? "" : saved.history(); target = -1;
        state = loaded; screen = "world"; slot = which; walking = false; replay = playReplay;
        replayHistory = saved.history(); notice = ""; rebuildTiles(); dirty = true;
    }

    private void act(char command) throws IOException {
        if (!state.get("status").equals("playing")) return;
        if (history.length() >= 20000) { notice = "Action limit reached. Press N for a new world."; return; }
        String next = history + Character.toUpperCase(command);
        Map<String, Object> result = engine.state(seed, next, target);
        history = next; state = result; notice = "";
        animationCount = Integer.MAX_VALUE;
        if (!state.get("status").equals("playing")) walking = false;
        rebuildTiles(); dirty = true;
    }

    private void key(char key) throws IOException {
        dirty = true;
        if (key == 27) {
            if (screen.equals("world")) { screen = "menu"; walking = replay = false; }
            else screen = returnScreen;
            notice = ""; return;
        }
        if (screen.equals("menu")) {
            if (key == 'n') newSeed();
            else if (key == 'l') load(1, false);
            else if (key == 'q') System.exit(0);
            else if (key == 'r' && state != null) screen = "world";
            else if (key == '?') { returnScreen = "menu"; screen = "help"; }
            return;
        }
        if (screen.equals("seed")) {
            if (key >= '0' && key <= '9' && seedText.length() < 10) seedText += key;
            else if ((key == '\b' || key == 127) && !seedText.isEmpty()) seedText = seedText.substring(0, seedText.length() - 1);
            else if (key == 's' && !seedText.isEmpty()) start();
            return;
        }
        if (screen.equals("help") || screen.equals("compare")) { screen = returnScreen; return; }
        if (screen.equals("slots")) {
            if (key >= '1' && key <= '3') slot = key - '0';
            else if (key == 's') { engine.save(slot, seed, history); notice = "Saved to slot " + slot; }
            else if (key == 'l') load(slot, false);
            else if (key == 'r') load(slot, true);
            return;
        }
        if (replay) { replay = false; notice = "Replay paused. Continue exploring."; return; }
        if (colon) {
            colon = false;
            if (key == 'q') { engine.save(1, seed, history); System.exit(0); }
            return;
        }
        if (key == ':') { colon = true; notice = ": (Q to save and quit)"; return; }
        if (key == 'e') { walking = !walking; return; }
        walking = false;
        if ("wasd".indexOf(key) >= 0) act(key);
        else if (key == ' ' || key == 'f') act('F');
        else if (key == '.') act('.');
        else if (key == 'u' || key == 'z') {
            if (!history.isEmpty()) { history = history.substring(0, history.length() - 1); refresh(); }
        } else if (key == 'n') newSeed();
        else if (key == 'l') { fog = !fog; rebuildTiles(); }
        else if (key == 'g') enemyPaths = !enemyPaths;
        else if (key == 'h') path = !path;
        else if (key == 'v') footprints = !footprints;
        else if (key == 'm') graph = !graph;
        else if (key >= '1' && key <= '3') algorithm = key - '1';
        else if (key == 't') { footprints = true; animationCount = 0; }
        else if (key == 'b') { returnScreen = "world"; screen = "compare"; }
        else if (key == 'p') { returnScreen = "world"; screen = "slots"; notice = ""; }
        else if (key == '?') { returnScreen = "world"; screen = "help"; }
    }

    private int mouseCell() {
        int x = (int) Math.floor(StdDraw.mouseX()), y = H - 1 - (int) Math.floor(StdDraw.mouseY() - OFFSET_Y);
        return x >= 0 && x < W && y >= 0 && y < H ? y * W + x : -1;
    }

    private void mouse() throws IOException {
        double y = StdDraw.mouseY();
        if (screen.equals("menu")) {
            if (Math.abs(StdDraw.mouseX() - W / 2.0) < 10) {
                if (Math.abs(y - 20) < 1) key('n');
                else if (Math.abs(y - 17.5) < 1) key('l');
                else if (Math.abs(y - 15) < 1) key('q');
            }
        } else if (screen.equals("world")) {
            walking = replay = false;
            int id = mouseCell();
            if (id < 0 || ints("tiles").get(id) == 0) return;
            if (fog && Json.number(list("visible").get(id)) == 0) { notice = "Target is outside line of sight."; dirty = true; return; }
            target = id; refresh(); animationCount = Integer.MAX_VALUE;
        }
    }

    private static int distance(int a, int b) { return Math.abs(a % W - b % W) + Math.abs(a / W - b / W); }

    private void step() throws IOException {
        if (replay) {
            if (history.length() == replayHistory.length()) { replay = false; notice = "Replay complete."; dirty = true; return; }
            history = replayHistory.substring(0, history.length() + 1); refresh(); return;
        }
        Map<String, Object> route = search(algorithm);
        if (route == null) { walking = false; notice = "Click a floor tile first."; dirty = true; return; }
        List<Integer> steps = ints(route.get("path"));
        if (steps.size() < 2 || !state.get("status").equals("playing")) { walking = false; return; }
        int next = steps.get(1);
        for (Object value : list("enemies")) {
            int at = Json.number(Json.object(value).get("at"));
            if (distance(at, next) <= 1) { walking = false; notice = "Guard nearby. Auto-walk stopped. SPACE to attack."; dirty = true; return; }
        }
        if (fog && Json.number(list("visible").get(next)) == 0) { walking = false; notice = "Unknown area. Auto-walk stopped."; dirty = true; return; }
        int before = number("player"), health = number("health"), delta = next - before;
        act(delta == 1 ? 'D' : delta == -1 ? 'A' : delta == W ? 'S' : 'W');
        if (number("player") == before || number("health") < health) walking = false;
    }

    private boolean wall(int id, List<Integer> ground) {
        int x = id % W, y = id / W;
        for (int dy = -1; dy <= 1; dy++) for (int dx = -1; dx <= 1; dx++) {
            int a = x + dx, b = y + dy;
            if (a >= 0 && a < W && b >= 0 && b < H && ground.get(b * W + a) > 0) return true;
        }
        return false;
    }

    private void rebuildTiles() {
        List<Integer> ground = ints("tiles"), visible = ints("visible"), explored = ints("explored");
        tiles = new TETile[W][H];
        for (int id = 0; id < W * H; id++) {
            TETile tile = ground.get(id) == 2 ? Tileset.SAND : ground.get(id) == 1 ? Tileset.FLOOR
                    : wall(id, ground) ? Tileset.WALL : Tileset.NOTHING;
            if (fog && visible.get(id) == 0) tile = explored.get(id) == 0 ? Tileset.NOTHING : new TETile(tile, Color.DARK_GRAY);
            put(id, tile);
        }
        putVisible(number("exit"), number("collected") == 4 ? Tileset.UNLOCKED_DOOR : Tileset.LOCKED_DOOR);
        for (int id : ints("crystals")) putVisible(id, Tileset.FLOWER);
        for (int id : ints("potions")) putVisible(id, HEAL);
        for (Object value : list("enemies")) putVisible(Json.number(Json.object(value).get("at")), GUARD);
        put(number("player"), Tileset.AVATAR);
    }

    private void put(int id, TETile tile) { tiles[id % W][H - 1 - id / W] = tile; }
    private void putVisible(int id, TETile tile) { if (!fog || Json.number(list("visible").get(id)) != 0) put(id, tile); }
    private double x(int id) { return id % W + .5; }
    private double y(int id) { return H - 1 - id / W + OFFSET_Y + .5; }
    private boolean visible(int id) { return !fog || Json.number(list("visible").get(id)) != 0; }

    private void routeLine(List<Integer> route, Color color) {
        StdDraw.setPenColor(color); StdDraw.setPenRadius(.0015);
        for (int i = 1; i < route.size(); i++) {
            int a = route.get(i - 1), b = route.get(i);
            if (visible(a) && visible(b)) StdDraw.line(x(a), y(a), x(b), y(b));
        }
        StdDraw.setPenRadius();
    }

    private void renderWorld() {
        renderer.resetFont(); renderer.drawTiles(tiles);
        Map<String, Object> route = search(algorithm);
        if (footprints && route != null) {
            List<Integer> order = ints(route.get("order"));
            StdDraw.setPenColor(new Color(70, 100, 70));
            for (int i = 0; i < Math.min(order.size(), animationCount); i++) {
                int id = order.get(i); if (visible(id)) StdDraw.filledCircle(x(id), y(id), .12);
            }
        }
        if (path && route != null) routeLine(ints(route.get("path")), Color.CYAN);
        if (enemyPaths) for (Object value : list("enemies")) routeLine(ints(Json.object(value).get("path")), Color.RED);
        if (graph) {
            for (Object value : list("edges")) {
                Map<String, Object> e = Json.object(value);
                int a = Json.number(Json.object(list("rooms").get(Json.number(e.get("a")))).get("center"));
                int b = Json.number(Json.object(list("rooms").get(Json.number(e.get("b")))).get("center"));
                routeLine(List.of(a, b), Boolean.TRUE.equals(e.get("tree")) ? Color.GREEN : Color.YELLOW);
            }
        }
        if (target >= 0 && visible(target)) { StdDraw.setPenColor(Color.CYAN); StdDraw.square(x(target), y(target), .45); }
        StdDraw.setFont(HUD); StdDraw.setPenColor(Color.WHITE);
        StdDraw.textLeft(1, H + 4, "HP " + number("health") + "/100   Flowers " + number("collected")
                + "/4   Turn " + number("turn") + "   Cost " + number("spent"));
        StdDraw.textRight(W - 1, H + 4, hovered >= 0 ? (visible(hovered)
                ? tiles[hovered % W][H - 1 - hovered / W].description() : "unknown") : "");
        StdDraw.setFont(SMALL);
        if (route != null) StdDraw.textLeft(1, H + 2.7, algorithmName(algorithm) + "  steps="
                + (ints(route.get("path")).size() - 1) + "  cost=" + Json.number(route.get("cost"))
                + "  expanded=" + Json.number(route.get("expanded")) + "   [B] compare");
        else StdDraw.textLeft(1, H + 2.7, "Seed " + seed + "   Click a floor tile to choose a path target.");
        StdDraw.textRight(W - 1, H + 2.7, "LOS " + (fog ? "ON" : "OFF") + "   " + (replay ? "REPLAY" : walking ? "AUTO" : ""));
        StdDraw.text(W / 2.0, 1.1, "WASD move | SPACE attack | L sight | G guards | 1/2/3 algorithm | E walk | ? help");
        StdDraw.setFont(new Font("Dialog", Font.PLAIN, 11));
        String message = !notice.isEmpty() ? notice : (String) state.get("message");
        if (replay) message = "Replay " + history.length() + "/" + replayHistory.length() + " (any key to stop)";
        if (!state.get("status").equals("playing")) message += "   [N] new world   [U] undo   [ESC] menu";
        StdDraw.text(W / 2.0, .25, message);
    }

    private static String algorithmName(int index) { return new String[]{"BFS", "Dijkstra", "A*"}[index]; }

    private void title(String text, double y) { StdDraw.setFont(TITLE); StdDraw.text(W / 2.0, y, text); }
    private void line(String text, double y) { StdDraw.setFont(MENU_FONT); StdDraw.text(W / 2.0, y, text); }
    private void small(String text, double y) { StdDraw.setFont(HUD); StdDraw.text(W / 2.0, y, text); }

    private void render() {
        StdDraw.clear(Color.BLACK); StdDraw.setPenColor(Color.WHITE);
        switch (screen) {
            case "world" -> renderWorld();
            case "menu" -> {
                title("CS 61B: The Game", 29);
                line("New Game (N)", 20);
                line("Load Game (L)", 17.5);
                line("Quit (Q)", 15);
                if (state != null) small("Resume (R)", 10);
                small("Help (?)", 6);
            }
            case "seed" -> {
                title("Enter Seed", 28);
                line(seedText + "_", 21);
                line("Press S to start", 15);
                small("0 .. 4294967295    BACKSPACE delete    ESC back", 10);
            }
            case "slots" -> {
                title("Save / Load", 31);
                for (int i = 1; i <= 3; i++) {
                    String detail = "empty";
                    if (engine.exists(i)) {
                        try { EngineBridge.Saved s = engine.load(i); detail = "seed " + s.seed() + ", actions " + s.history().length(); }
                        catch (Exception error) { detail = "invalid save"; }
                    }
                    small((slot == i ? "> " : "  ") + "Slot " + i + ": " + detail, 25 - i * 3);
                }
                small("1 / 2 / 3 select slot", 11);
                small("S save    L load    R replay    ESC return", 8);
            }
            case "compare" -> {
                title("Pathfinding", 32);
                small("Same start / target. Sand costs 5; floor costs 1.", 28);
                small("Algorithm       Steps       Cost       Expanded", 24);
                for (int i = 0; i < 3; i++) {
                    Map<String, Object> result = search(i);
                    if (result != null) small(String.format("%-12s %7d %10d %12d", algorithmName(i),
                            ints(result.get("path")).size() - 1, Json.number(result.get("cost")),
                            Json.number(result.get("expanded"))), 21 - i * 3);
                }
                small("BFS minimizes steps. Dijkstra / A* minimize cost.", 9);
                small("Press any key to return", 5);
            }
            case "help" -> {
                title("Controls", 34);
                String[] help = {"Collect 4 flowers, then reach the orange door.",
                    "@ you    # wall    . floor    sand cost 5    g guard    + health",
                    "WASD / arrows : move       SPACE / F : attack       . : wait",
                    "Guards act every 3 turns; two adjacent attacks defeat a guard.",
                    "Click floor : target       1 BFS / 2 Dijkstra / 3 A*",
                    "E : auto-walk / stop       H : player path       G : guard paths",
                    "V : expanded nodes        T : animate search    B : compare",
                    "L : line of sight         M : room graph (green=MST, yellow=extra)",
                    "U / Z : undo              P : save slots        N : new world",
                    ":Q : save slot 1 and quit                       ESC : menu",
                    "World generation: Kruskal MST + disjoint set + 3 extra edges.",
                    "Pathfinding uses C++ adjacency lists, ring queue and min-heap."};
                for (int i = 0; i < help.length; i++) small(help[i], 29 - i * 1.8);
                small("Press any key to return", 3);
            }
            default -> throw new IllegalStateException("Unknown screen " + screen);
        }
        if (!notice.isEmpty() && !screen.equals("world")) {
            StdDraw.setFont(SMALL); StdDraw.setPenColor(Color.YELLOW); StdDraw.text(W / 2.0, 2, notice);
        }
        StdDraw.show();
    }
}
