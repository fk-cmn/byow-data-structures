import core.EngineBridge;
import core.Json;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.Map;

/** 不启动 GUI，验证真实 C++ 子进程与 Java 原版渲染层之间的边界。 */
public final class BridgeTests {
    private static int checks;
    private static void require(boolean value, String message) {
        checks++;
        if (!value) throw new AssertionError(message);
    }
    public static void main(String[] args) throws Exception {
        Path root=Path.of(args[0]);
        Path temporary=Files.createTempDirectory(root.resolve("build"),"bridge-tests-");
        String binary=System.getProperty("os.name").startsWith("Windows")?"relic_engine.exe":"relic_engine";
        Files.createDirectories(temporary.resolve("build"));
        Path copy=temporary.resolve("build").resolve(binary);
        Files.copy(root.resolve("build").resolve(binary),copy,StandardCopyOption.COPY_ATTRIBUTES);
        EngineBridge bridge=new EngineBridge(temporary);
        try {
            Map<String,Object> parsed=Json.object(Json.parse("{\"text\":\"中文\\n\\u0041\",\"list\":[true,false,null,-1,1.2e2]}"));
            require(parsed.get("text").equals("中文\nA"),"JSON strings/escapes");
            require(Json.array(parsed.get("list")).size()==5,"JSON literals and numbers");
            var initial=bridge.state(2026,"",-1);
            require(Json.number(initial.get("width"))==57,"C++ grid dimensions");
            for(int slot=1;slot<=3;slot++){
                String history=slot==1?"":"WASDF.WASDF..";
                bridge.save(slot,4294967295L,history);
                var saved=bridge.load(slot);
                require(saved.seed()==4294967295L&&saved.history().equals(history),"save slots including empty history");
                require(bridge.state(saved.seed(),saved.history(),-1).equals(bridge.state(4294967295L,history,-1)),"save/load exact state");
            }
            boolean rejected=false;try{EngineBridge.validate(-1,"");}catch(IllegalArgumentException e){rejected=true;}
            require(rejected,"negative seed rejected");
            rejected=false;try{EngineBridge.validate(0,"invalid");}catch(IllegalArgumentException e){rejected=true;}
            require(rejected,"malformed action sequence rejected");
            Files.writeString(temporary.resolve("saves/slot1.txt"),"broken");
            rejected=false;try{bridge.load(1);}catch(Exception e){rejected=true;}
            require(rejected,"corrupt save rejected");
            int target=Json.number(Json.array(initial.get("crystals")).get(0));
            var planned=bridge.state(2026,"",target);
            require(Json.array(planned.get("searches")).size()==3,"all algorithms available through bridge");
            System.out.println("PASS: Java/C++ bridge, JSON, saves, validation ("+checks+" assertions)");
        } finally {
            try(var paths=Files.walk(temporary)) {
                for(Path p:paths.sorted(java.util.Comparator.reverseOrder()).toList())Files.deleteIfExists(p);
            }
        }
    }
}
