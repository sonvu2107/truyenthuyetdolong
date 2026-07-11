#!/usr/bin/env node
"use strict";

// Runtime dự phòng cho máy build Windows chỉ có Node.js. Định dạng và các
// kiểm tra tương đương phần apply/validate của cbp_localizer.py.
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const CBP_MAGIC = 5259843;
const CBP_VERSION = 17435658;
const HEADER_SIZE = 64;
const routePathPattern = /(?:^|\.)(?:comp|prom)\.(?:scene|npc)$|\.target\.\d+\.location\.(?:entityName|sceneName)$/;
const moveLinkPattern = /<[^<>]*\/M([^<>]*)>/g;

function fail(message) {
  throw new Error(message);
}

class Reader {
  constructor(payload) {
    this.payload = payload;
    this.position = 0;
    this.nodeCount = 0;
  }

  take(size) {
    if (size < 0 || this.position + size > this.payload.length) {
      fail(`Đọc tràn tại byte ${this.position}: cần ${size}, payload có ${this.payload.length} byte`);
    }
    const result = this.payload.subarray(this.position, this.position + size);
    this.position += size;
    return result;
  }

  readNode(depth = 0) {
    if (depth > 2000) fail("Cây CBP lồng quá sâu");
    const nameSize = this.take(1)[0];
    const kind = this.take(1)[0];
    this.nodeCount += 1;
    if (kind === 0 || kind === 1 || kind === 2) {
      const rawValue = Buffer.from(this.take(8));
      const name = this.take(nameSize).toString("utf8");
      return { name, kind, rawValue };
    }
    if (kind !== 3 && kind !== 4) fail(`Kiểu node CBP không hợp lệ: ${kind}`);
    const value = this.take(4).readUInt32LE(0);
    const padding = Buffer.from(this.take(4));
    const name = this.take(nameSize).toString("utf8");
    if (kind === 3) {
      return { name, kind, padding, text: this.take(value).toString("utf8") };
    }
    const children = [];
    for (let i = 0; i < value; i += 1) children.push(this.readNode(depth + 1));
    return { name, kind, padding, children };
  }
}

function decodeCbp(data) {
  if (data.length < HEADER_SIZE) fail("File ngắn hơn header CBP 64 byte");
  const magic = data.readUInt32LE(0);
  const version = data.readUInt32LE(4);
  const unpackedSize = data.readUInt32LE(8);
  const packedSize = data.readUInt32LE(12);
  if (magic !== CBP_MAGIC) fail(`Sai magic CBP: ${magic}`);
  if (version !== CBP_VERSION) fail(`Sai phiên bản CBP: ${version}`);
  if (data.length < HEADER_SIZE + packedSize) fail("Luồng zlib CBP bị thiếu");
  const payload = zlib.inflateSync(data.subarray(HEADER_SIZE, HEADER_SIZE + packedSize));
  if (payload.length !== unpackedSize) {
    fail(`Kích thước payload sai: header=${unpackedSize}, thực tế=${payload.length}`);
  }
  const reader = new Reader(payload);
  const root = reader.readNode();
  if (reader.position !== payload.length) {
    fail(`Payload còn dư ${payload.length - reader.position} byte`);
  }
  return { header: Buffer.from(data.subarray(0, HEADER_SIZE)), root, nodeCount: reader.nodeCount };
}

function encodeNode(node) {
  const name = Buffer.from(node.name, "utf8");
  if (name.length > 255) fail(`Tên node dài hơn 255 byte: ${node.name}`);
  const prefix = Buffer.from([name.length, node.kind]);
  if (node.kind === 0 || node.kind === 1 || node.kind === 2) {
    if (!node.rawValue || node.rawValue.length !== 8) fail(`Node ${node.name} thiếu 8 byte dữ liệu`);
    return Buffer.concat([prefix, node.rawValue, name]);
  }
  if (node.kind === 3) {
    const value = Buffer.from(node.text, "utf8");
    const size = Buffer.alloc(4);
    size.writeUInt32LE(value.length, 0);
    return Buffer.concat([prefix, size, node.padding, name, value]);
  }
  if (node.kind === 4) {
    const size = Buffer.alloc(4);
    size.writeUInt32LE(node.children.length, 0);
    return Buffer.concat([prefix, size, node.padding, name, ...node.children.map(encodeNode)]);
  }
  fail(`Không thể ghi kiểu node ${node.kind}`);
}

function encodeCbp(header, root) {
  const payload = encodeNode(root);
  const compressed = zlib.deflateSync(payload, { level: 9 });
  const outputHeader = Buffer.from(header);
  outputHeader.writeUInt32LE(CBP_MAGIC, 0);
  outputHeader.writeUInt32LE(CBP_VERSION, 4);
  outputHeader.writeUInt32LE(payload.length, 8);
  outputHeader.writeUInt32LE(compressed.length, 12);
  return Buffer.concat([outputHeader, compressed]);
}

function walkStrings(node, parent = "", output = new Map()) {
  const current = parent && node.name ? `${parent}.${node.name}` : (node.name || parent);
  if (node.kind === 3) output.set(current, node);
  if (node.kind === 4) node.children.forEach(child => walkStrings(child, current, output));
  return output;
}

function movePayloads(text) {
  const payloads = [];
  moveLinkPattern.lastIndex = 0;
  let match;
  while ((match = moveLinkPattern.exec(text)) !== null) payloads.push(match[1]);
  return payloads;
}

function validateTranslation(fileName, nodePath, source, target) {
  if (String(fileName).toLowerCase() !== "stdquest.cbp") return;
  if (routePathPattern.test(nodePath) && target !== source) {
    fail(`Không được dịch khóa định tuyến nhiệm vụ tại ${nodePath}`);
  }
  const sourcePayloads = movePayloads(source);
  const targetPayloads = movePayloads(target);
  if (JSON.stringify(sourcePayloads) !== JSON.stringify(targetPayloads)) {
    fail(`Payload /M bị thay đổi tại ${nodePath}`);
  }
}

function applyCatalog(input, catalog) {
  if (catalog.format !== 1 || !catalog.translations || typeof catalog.translations !== "object") {
    fail("Catalog không đúng format 1");
  }
  const decoded = decodeCbp(input);
  const strings = walkStrings(decoded.root);
  let changed = 0;
  for (const [nodePath, entry] of Object.entries(catalog.translations)) {
    const node = strings.get(nodePath);
    if (!node) fail(`Catalog tham chiếu node không tồn tại: ${nodePath}`);
    if (typeof entry.source !== "string" || typeof entry.target !== "string") {
      fail(`Mục catalog không hợp lệ: ${nodePath}`);
    }
    if (node.text !== entry.source) {
      fail(`Câu gốc không khớp tại ${nodePath}: CBP=${JSON.stringify(node.text)}, catalog=${JSON.stringify(entry.source)}`);
    }
    validateTranslation(catalog.file, nodePath, entry.source, entry.target);
    if (node.text !== entry.target) {
      node.text = entry.target;
      changed += 1;
    }
  }
  const output = encodeCbp(decoded.header, decoded.root);
  const checked = decodeCbp(output);
  if (checked.nodeCount !== decoded.nodeCount) fail("Số node thay đổi sau khi ghi CBP");
  return { output, changed, nodeCount: checked.nodeCount };
}

function listCbpFiles(root) {
  const output = [];
  for (const name of fs.readdirSync(root)) {
    const full = path.join(root, name);
    const stat = fs.statSync(full);
    if (stat.isDirectory()) output.push(...listCbpFiles(full));
    else if (name.toLowerCase().endsWith(".cbp")) output.push(full);
  }
  return output;
}

function main() {
  const [command, ...args] = process.argv.slice(2);
  if (command === "apply" && args.length === 3) {
    const [inputPath, catalogPath, outputPath] = args;
    const catalog = JSON.parse(fs.readFileSync(catalogPath, "utf8"));
    const result = applyCatalog(fs.readFileSync(inputPath), catalog);
    fs.writeFileSync(outputPath, result.output);
    console.log(`Đã biên dịch ${outputPath}: đổi ${result.changed} chuỗi trong ${result.nodeCount} node`);
    return;
  }
  if (command === "validate" && args.length === 1) {
    const checked = decodeCbp(fs.readFileSync(args[0]));
    console.log(`CBP hợp lệ: ${args[0]} (${checked.nodeCount} node)`);
    return;
  }
  if (command === "validate-catalog" && args.length === 1) {
    const catalog = JSON.parse(fs.readFileSync(args[0], "utf8"));
    if (catalog.format !== 1 || !catalog.translations || typeof catalog.translations !== "object") {
      fail("Catalog không đúng format 1");
    }
    for (const [nodePath, entry] of Object.entries(catalog.translations)) {
      if (typeof entry.source !== "string" || typeof entry.target !== "string") {
        fail(`Mục catalog không hợp lệ: ${nodePath}`);
      }
      validateTranslation(catalog.file, nodePath, entry.source, entry.target);
    }
    console.log(`Catalog hợp lệ: ${args[0]} (${Object.keys(catalog.translations).length} mục)`);
    return;
  }
  if (command === "validate-dir" && args.length === 1) {
    const files = listCbpFiles(args[0]);
    let nodes = 0;
    files.forEach(file => { nodes += decodeCbp(fs.readFileSync(file)).nodeCount; });
    console.log(`CBP hợp lệ: ${files.length} file, ${nodes} node`);
    return;
  }
  fail("Cách dùng: cbp_node_runtime.js apply <input.cbp> <catalog.json> <output.cbp> | validate <file.cbp> | validate-catalog <catalog.json> | validate-dir <folder>");
}

try {
  main();
} catch (error) {
  console.error(`LỖI: ${error.message}`);
  process.exitCode = 1;
}
