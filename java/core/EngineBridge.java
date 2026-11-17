package core;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.nio.file.AtomicMoveNotSupportedException;
import java.util.List;
import java.util.Map;

/** Java 只负责原版 TileEngine 输入和显示；所有数据结构算法在 src/ 的 C++ 中运行。 */
public final class EngineBridge {
    private final Path root;
    private final Path binary;
    private final Path saves;

    public record Saved(long seed, String history) { }

    public EngineBridge(Path root) {
        this.root = root;
        binary = root.resolve("build").resolve(System.getProperty("os.name").startsWith("Windows")
                ? "relic_engine.exe" : "relic_engine");
        // macOS app 内部只放资源，存档放在 .app 同级目录，便于拷贝与备份。
        boolean appBundle = root.getFileName().toString().equals("app") && root.getParent() != null
                && root.getParent().getFileName().toString().equals("Contents");
        saves = (appBundle ? root.getParent().getParent().getParent() : root).resolve("saves");
    }

    public static void validate(long seed, String history) {
        if (seed < 0 || seed > 4294967295L) throw new IllegalArgumentException("Seed must be 0..4294967295");
        if (history.length() > 20000 || !history.matches("[WASDF.]*")) {
            throw new IllegalArgumentException("Invalid action history (max 20000)");
        }
    }

    public Map<String, Object> state(long seed, String history, int target) throws IOException {
        validate(seed, history);
        Process process = new ProcessBuilder(binary.toString(), Long.toString(seed), history,
                Integer.toString(target)).redirectError(ProcessBuilder.Redirect.INHERIT).start();
        String json = new String(process.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
        try {
            if (process.waitFor() != 0) throw new IOException("C++ engine failed");
        } catch (InterruptedException error) {
            Thread.currentThread().interrupt(); process.destroyForcibly(); throw new IOException(error);
        }
        return Json.object(Json.parse(json));
    }

    private Path slot(int slot) {
        if (slot < 1 || slot > 3) throw new IllegalArgumentException("Slot must be 1..3");
        return saves.resolve("slot" + slot + ".txt");
    }

    public boolean exists(int slot) { return Files.isRegularFile(slot(slot)); }

    public void save(int slot, long seed, String history) throws IOException {
        validate(seed, history);
        Path file = slot(slot); Files.createDirectories(file.getParent());
        Path temp = Files.createTempFile(file.getParent(), "byow-", ".tmp");
        try {
            Files.writeString(temp, "BYOW-CXX-1\n" + seed + "\n" + history + "\n", StandardCharsets.UTF_8);
            try {
                Files.move(temp, file, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
            } catch (AtomicMoveNotSupportedException error) {
                Files.move(temp, file, StandardCopyOption.REPLACE_EXISTING);
            }
        } finally { Files.deleteIfExists(temp); }
    }

    public Saved load(int slot) throws IOException {
        Path file = slot(slot);
        if (Files.size(file) > 21000) throw new IOException("Save file too large");
        List<String> lines = Files.readAllLines(file, StandardCharsets.UTF_8);
        if (lines.size() != 3 || !lines.get(0).equals("BYOW-CXX-1")) throw new IOException("Invalid save file");
        long seed = Long.parseLong(lines.get(1)); String history = lines.get(2);
        validate(seed, history); return new Saved(seed, history);
    }
}
