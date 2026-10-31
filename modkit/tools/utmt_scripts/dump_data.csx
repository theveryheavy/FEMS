using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using UndertaleModLib;
using UndertaleModLib.Models;
using UndertaleModLib.Util;

EnsureDataLoaded();
string root = Environment.GetEnvironmentVariable("FEDUMP_OUT");
if (string.IsNullOrWhiteSpace(root)) root = Path.Combine(Path.GetTempPath(), "fedump");
Directory.CreateDirectory(root);
var jo = new JsonSerializerOptions { WriteIndented = true, DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull };
var seen = new HashSet<object>(ReferenceEqualityComparer.Instance);

object N(object o, int d)
{
    if (o == null) return null;
    if (o is string || o is bool || o is int || o is long || o is float || o is double || o is uint || o is ushort || o is short || o is byte || o is sbyte || o is ulong || o is decimal) return o;
    if (o is Enum) return o.ToString();
    if (o is UndertaleString us) return us.Content;
    var t = o.GetType();
    var np = t.GetProperty("Name");
    if (np != null && np.PropertyType == typeof(UndertaleString)) { var nv = np.GetValue(o) as UndertaleString; if (nv != null && d > 0 && t.Namespace != null && t.Namespace.StartsWith("UndertaleModLib")) return "<" + t.Name + ":" + nv.Content + ">"; }
    if (d > 6) return "<maxdepth>";
    if (o is IDictionary dict) { var dd = new Dictionary<string, object>(); foreach (DictionaryEntry e in dict) dd[Convert.ToString(e.Key)] = N(e.Value, d + 1); return dd; }
    if (o is IEnumerable en) { var l = new List<object>(); int i = 0; foreach (var x in en) { if (i++ > 20000) { l.Add("<truncated>"); break; } l.Add(N(x, d + 1)); } return l; }
    if (t.Namespace != null && t.Namespace.StartsWith("UndertaleModLib"))
    {
        if (!seen.Add(o)) return "<ref>";
        var dd = new Dictionary<string, object>();
        foreach (var p in t.GetProperties(BindingFlags.Public | BindingFlags.Instance))
        {
            if (p.GetIndexParameters().Length > 0) continue;
            try { dd[p.Name] = N(p.GetValue(o), d + 1); } catch { }
        }
        return dd;
    }
    return o.ToString();
}
void W(string rel, string txt) { string f = Path.Combine(root, rel); Directory.CreateDirectory(Path.GetDirectoryName(f)); File.WriteAllText(f, txt, new UTF8Encoding(false)); }
void J(string rel, object obj) { seen.Clear(); W(rel, JsonSerializer.Serialize(obj, jo)); }
Console.WriteLine("[dump] -> " + root);

var gi = Data.GeneralInfo;
var mi = new Dictionary<string, object>();
void Put(string k, Func<object> f) { try { mi[k] = f(); } catch (Exception e) { mi[k] = "ERR: " + e.Message; } }
Put("IsGMS2", () => Data.IsGameMaker2());
Put("IsYYC", () => Data.IsYYC());
Put("BytecodeVersion", () => gi.BytecodeVersion);
Put("Name", () => gi.Name == null ? null : gi.Name.Content);
Put("DisplayName", () => gi.DisplayName == null ? null : gi.DisplayName.Content);
Put("FileName", () => gi.FileName == null ? null : gi.FileName.Content);
Put("Config", () => gi.Config == null ? null : gi.Config.Content);
Put("Version", () => gi.Version.Major + "." + gi.Version.Minor + "." + gi.Version.Release + "." + gi.Version.Build);
Put("GameID", () => gi.GameID);
Put("SteamAppID", () => gi.SteamAppID);
Put("GUID", () => gi.GMS2GameGUID == null ? null : gi.GMS2GameGUID.ToString());
Put("Window", () => gi.DefaultWindowWidth + "x" + gi.DefaultWindowHeight);
Put("FPS", () => gi.GMS2FPS);
Put("RoomOrder", () => gi.RoomOrder == null ? null : gi.RoomOrder.Where(r => r != null && r.Resource != null).Select(r => r.Resource.Name.Content).ToList());
Put("Strings", () => Data.Strings.Count);
Put("Sprites", () => Data.Sprites.Count);
Put("Backgrounds", () => Data.Backgrounds.Count);
Put("Fonts", () => Data.Fonts.Count);
Put("Sounds", () => Data.Sounds.Count);
Put("AudioGroups", () => Data.AudioGroups == null ? -1 : Data.AudioGroups.Count);
Put("Shaders", () => Data.Shaders.Count);
Put("Objects", () => Data.GameObjects.Count);
Put("Rooms", () => Data.Rooms.Count);
Put("Code", () => Data.Code.Count);
Put("TexturePageItems", () => Data.TexturePageItems.Count);
Put("EmbeddedTextures", () => Data.EmbeddedTextures.Count);
Put("EmbeddedAudio", () => Data.EmbeddedAudio == null ? -1 : Data.EmbeddedAudio.Count);
Put("Paths", () => Data.Paths.Count);
Put("Extensions", () => Data.Extensions == null ? -1 : Data.Extensions.Count);
Put("Variables", () => Data.Variables == null ? -1 : Data.Variables.Count);
Put("Constants", () => Data.Options == null || Data.Options.Constants == null ? null : Data.Options.Constants.Select(c => new { Name = c.Name == null ? null : c.Name.Content, Value = c.Value == null ? null : c.Value.Content }).ToList());
J("meta.json", mi);

var sl = new List<object>();
for (int i = 0; i < Data.Strings.Count; i++) { var s = Data.Strings[i]; if (s != null) sl.Add(new { id = i, text = s.Content }); }
J("strings.json", sl);

var tl = new List<object>();
Directory.CreateDirectory(Path.Combine(root, "textures"));
for (int i = 0; i < Data.EmbeddedTextures.Count; i++)
{
    var tex = Data.EmbeddedTextures[i]; if (tex == null) continue;
    string nm = tex.Name == null ? "tex_" + i : tex.Name.Content;
    var td = tex.TextureData;
    tl.Add(new { id = i, name = nm, width = td == null ? 0 : td.Width, height = td == null ? 0 : td.Height, format = td == null || td.Image == null ? "null" : td.Image.Format.ToString() });
    try { if (td != null && td.Image != null) using (var fs = File.Create(Path.Combine(root, "textures", nm + ".png"))) td.Image.SavePng(fs); }
    catch (Exception e) { Console.WriteLine("[tex] " + nm + ": " + e.Message); }
}
J("textures.json", tl);
Console.WriteLine("[dump] part1 ok");

var spl = new List<object>();
using (var w = new TextureWorker())
{
    for (int i = 0; i < Data.Sprites.Count; i++)
    {
        var spr = Data.Sprites[i]; if (spr == null) continue;
        string nm = spr.Name.Content; string dir = Path.Combine(root, "sprites", nm); Directory.CreateDirectory(dir);
        var fr = new List<object>();
        for (int f = 0; f < spr.Textures.Count; f++)
        {
            var tpi = spr.Textures[f] == null ? null : spr.Textures[f].Texture;
            if (tpi != null) { try { w.ExportAsPNG(tpi, Path.Combine(dir, f + ".png")); } catch (Exception e) { Console.WriteLine("[spr] " + nm + " " + f + ": " + e.Message); } }
            fr.Add(new { i = f, page = tpi == null || tpi.TexturePage == null || tpi.TexturePage.Name == null ? null : tpi.TexturePage.Name.Content, pageIndex = tpi == null || tpi.TexturePage == null ? -1 : Data.EmbeddedTextures.IndexOf(tpi.TexturePage), x = tpi == null ? 0 : tpi.SourceX, y = tpi == null ? 0 : tpi.SourceY, w = tpi == null ? 0 : tpi.SourceWidth, h = tpi == null ? 0 : tpi.SourceHeight, tx = tpi == null ? 0 : tpi.TargetX, ty = tpi == null ? 0 : tpi.TargetY, tw = tpi == null ? 0 : tpi.TargetWidth, th = tpi == null ? 0 : tpi.TargetHeight });
        }
        spl.Add(new { id = i, name = nm, width = spr.Width, height = spr.Height, ox = spr.OriginX, oy = spr.OriginY, ml = spr.MarginLeft, mr = spr.MarginRight, mb = spr.MarginBottom, mt = spr.MarginTop, transparent = spr.Transparent, smooth = spr.Smooth, bboxMode = spr.BBoxMode.ToString(), sepMasks = spr.SepMasks.ToString(), type = spr.SSpriteType.ToString(), speed = spr.GMS2PlaybackSpeed, speedType = spr.GMS2PlaybackSpeedType.ToString(), frames = fr });
    }
}
J("sprites.json", spl);
Console.WriteLine("[dump] sprites " + spl.Count);

var fl = new List<object>();
Directory.CreateDirectory(Path.Combine(root, "fonts"));
using (var w2 = new TextureWorker())
{
    for (int i = 0; i < Data.Fonts.Count; i++)
    {
        var fnt = Data.Fonts[i]; if (fnt == null) continue;
        string nm = fnt.Name.Content;
        if (fnt.Texture != null) { try { w2.ExportAsPNG(fnt.Texture, Path.Combine(root, "fonts", nm + ".png")); } catch (Exception e) { Console.WriteLine("[fnt] " + nm + ": " + e.Message); } }
        fl.Add(new { id = i, name = nm, displayName = fnt.DisplayName == null ? null : fnt.DisplayName.Content, emSize = fnt.EmSize, bold = fnt.Bold, italic = fnt.Italic, rangeStart = fnt.RangeStart, rangeEnd = fnt.RangeEnd, charset = fnt.Charset, aa = fnt.AntiAliasing, scaleX = fnt.ScaleX, scaleY = fnt.ScaleY, lineHeight = fnt.LineHeight, ascender = fnt.Ascender, ascenderOffset = fnt.AscenderOffset, sdfSpread = fnt.SDFSpread,
            glyphs = fnt.Glyphs == null ? null : fnt.Glyphs.Select(g => new { ch = g.Character, x = g.SourceX, y = g.SourceY, w = g.SourceWidth, h = g.SourceHeight, shift = g.Shift, offset = g.Offset }).ToList() });
    }
}
J("fonts.json", fl);

var shl = new List<object>();
Directory.CreateDirectory(Path.Combine(root, "shaders"));
for (int i = 0; i < Data.Shaders.Count; i++)
{
    var sh = Data.Shaders[i]; if (sh == null) continue;
    string d = Path.Combine(root, "shaders", sh.Name.Content); Directory.CreateDirectory(d);
    W(Path.Combine("shaders", sh.Name.Content, "type.txt"), sh.Type.ToString());
    W(Path.Combine("shaders", sh.Name.Content, "vertex_glsl_es.txt"), sh.GLSL_ES_Vertex == null ? "" : sh.GLSL_ES_Vertex.Content);
    W(Path.Combine("shaders", sh.Name.Content, "fragment_glsl_es.txt"), sh.GLSL_ES_Fragment == null ? "" : sh.GLSL_ES_Fragment.Content);
    W(Path.Combine("shaders", sh.Name.Content, "vertex_glsl.txt"), sh.GLSL_Vertex == null ? "" : sh.GLSL_Vertex.Content);
    W(Path.Combine("shaders", sh.Name.Content, "fragment_glsl.txt"), sh.GLSL_Fragment == null ? "" : sh.GLSL_Fragment.Content);
    W(Path.Combine("shaders", sh.Name.Content, "vertex_hlsl9.txt"), sh.HLSL9_Vertex == null ? "" : sh.HLSL9_Vertex.Content);
    W(Path.Combine("shaders", sh.Name.Content, "fragment_hlsl9.txt"), sh.HLSL9_Fragment == null ? "" : sh.HLSL9_Fragment.Content);
    shl.Add(new { id = i, name = sh.Name.Content, type = sh.Type.ToString(), attrs = sh.VertexShaderAttributes == null ? null : sh.VertexShaderAttributes.Select(a => a == null || a.Name == null ? null : a.Name.Content).ToList() });
}
J("shaders.json", shl);
Console.WriteLine("[dump] shaders " + shl.Count);

List<object> L<T>(IEnumerable<T> src, Func<T, int, object> f) where T : class
{
    var r = new List<object>();
    if (src == null) return r;
    int i = 0;
    foreach (var x in src) { if (x != null) { try { r.Add(f(x, i)); } catch (Exception e) { r.Add(new { id = i, error = e.Message }); } } i++; }
    return r;
}
J("sounds.json", L(Data.Sounds, (s, i) => new { id = i, data = N(s, 0) }));
J("audiogroups.json", L(Data.AudioGroups, (g, i) => new { id = i, data = N(g, 0) }));
J("objects.json", L(Data.GameObjects, (o, i) => new { id = i, data = N(o, 0) }));
J("rooms.json", L(Data.Rooms, (r, i) => new { id = i, data = N(r, 0) }));
J("code.json", L(Data.Code, (c, i) => new { id = i, name = c.Name == null ? null : c.Name.Content, instr = c.Instructions == null ? 0 : c.Instructions.Count, locals = c.LocalsCount, args = c.ArgumentsCount }));
J("variables.json", L(Data.Variables, (v, i) => new { id = i, name = v.Name == null ? null : v.Name.Content, type = v.InstanceType.ToString(), varId = v.VarID }));
J("paths.json", L(Data.Paths, (p, i) => new { id = i, data = N(p, 0) }));
J("backgrounds.json", L(Data.Backgrounds, (b, i) => new { id = i, data = N(b, 0) }));
J("extensions.json", L(Data.Extensions, (e, i) => new { id = i, data = N(e, 0) }));
Console.WriteLine("[dump] DONE");
