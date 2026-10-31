// False Echo Mod Kit - applies a JSON patch plan to data.win
using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Collections.Generic;
using UndertaleModLib;
using UndertaleModLib.Models;
using UndertaleModLib.Util;

EnsureDataLoaded();

string planPath = Environment.GetEnvironmentVariable("FEDK_PATCH");
if (string.IsNullOrWhiteSpace(planPath) || !File.Exists(planPath))
{
    Console.WriteLine("[fedk] no patch plan (FEDK_PATCH)");
    return;
}
var doc = JsonDocument.Parse(File.ReadAllText(planPath, Encoding.UTF8));
var root = doc.RootElement;
int nStr = 0, nTex = 0, nShd = 0;

if (root.TryGetProperty("strings", out var strings) && strings.ValueKind == JsonValueKind.Array)
{
    foreach (var e in strings.EnumerateArray())
    {
        int idx = e.GetProperty("index").GetInt32();
        string text = e.GetProperty("text").GetString();
        if (idx < 0 || idx >= Data.Strings.Count) { Console.WriteLine("[fedk] bad string index " + idx); continue; }
        Data.Strings[idx].Content = text;
        nStr++;
    }
}

if (root.TryGetProperty("textures", out var texs) && texs.ValueKind == JsonValueKind.Array)
{
    foreach (var e in texs.EnumerateArray())
    {
        int idx = e.GetProperty("index").GetInt32();
        string png = e.GetProperty("png").GetString();
        if (idx < 0 || idx >= Data.EmbeddedTextures.Count) { Console.WriteLine("[fedk] bad texture index " + idx); continue; }
        if (!File.Exists(png)) { Console.WriteLine("[fedk] missing png " + png); continue; }
        var tex = Data.EmbeddedTextures[idx];
        var img = GMImage.FromPng(File.ReadAllBytes(png));
        if (img.Width != tex.TextureData.Width || img.Height != tex.TextureData.Height)
            Console.WriteLine("[fedk] WARN texture " + idx + " resized " + tex.TextureData.Width + "x" + tex.TextureData.Height + " -> " + img.Width + "x" + img.Height);
        tex.TextureData.Image = img;
        nTex++;
    }
}

if (root.TryGetProperty("shaders", out var shds) && shds.ValueKind == JsonValueKind.Array)
{
    foreach (var e in shds.EnumerateArray())
    {
        string name = e.GetProperty("name").GetString();
        var sh = Data.Shaders.ByName(name);
        if (sh is null) { Console.WriteLine("[fedk] no shader " + name); continue; }
        if (e.TryGetProperty("vertex_glsl_es", out var v1)) sh.GLSL_ES_Vertex = new UndertaleString(File.ReadAllText(v1.GetString()));
        if (e.TryGetProperty("fragment_glsl_es", out var f1)) sh.GLSL_ES_Fragment = new UndertaleString(File.ReadAllText(f1.GetString()));
        if (e.TryGetProperty("vertex_glsl", out var v2)) sh.GLSL_Vertex = new UndertaleString(File.ReadAllText(v2.GetString()));
        if (e.TryGetProperty("fragment_glsl", out var f2)) sh.GLSL_Fragment = new UndertaleString(File.ReadAllText(f2.GetString()));
        if (e.TryGetProperty("vertex_hlsl9", out var v3)) sh.HLSL9_Vertex = new UndertaleString(File.ReadAllText(v3.GetString()));
        if (e.TryGetProperty("fragment_hlsl9", out var f3)) sh.HLSL9_Fragment = new UndertaleString(File.ReadAllText(f3.GetString()));
        nShd++;
    }
}

Console.WriteLine("[fedk] applied strings=" + nStr + " textures=" + nTex + " shaders=" + nShd);
