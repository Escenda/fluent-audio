/*eslint-disable block-scoped-var, id-length, no-control-regex, no-magic-numbers, no-prototype-builtins, no-redeclare, no-shadow, no-var, sort-vars*/
"use strict";

var $protobuf = require("protobufjs/minimal");

// Common aliases
var $Reader = $protobuf.Reader, $Writer = $protobuf.Writer, $util = $protobuf.util;

// Exported root namespace
var $root = $protobuf.roots["default"] || ($protobuf.roots["default"] = {});

$root.fluent_audio = (function() {

    /**
     * Namespace fluent_audio.
     * @exports fluent_audio
     * @namespace
     */
    var fluent_audio = {};

    fluent_audio.v1 = (function() {

        /**
         * Namespace v1.
         * @memberof fluent_audio
         * @namespace
         */
        var v1 = {};

        /**
         * SampleFormat enum.
         * @name fluent_audio.v1.SampleFormat
         * @enum {number}
         * @property {number} SAMPLE_FORMAT_UNSPECIFIED=0 SAMPLE_FORMAT_UNSPECIFIED value
         * @property {number} SAMPLE_FORMAT_S16LE=1 SAMPLE_FORMAT_S16LE value
         * @property {number} SAMPLE_FORMAT_F32LE=2 SAMPLE_FORMAT_F32LE value
         */
        v1.SampleFormat = (function() {
            var valuesById = {}, values = Object.create(valuesById);
            values[valuesById[0] = "SAMPLE_FORMAT_UNSPECIFIED"] = 0;
            values[valuesById[1] = "SAMPLE_FORMAT_S16LE"] = 1;
            values[valuesById[2] = "SAMPLE_FORMAT_F32LE"] = 2;
            return values;
        })();

        /**
         * ChannelLayout enum.
         * @name fluent_audio.v1.ChannelLayout
         * @enum {number}
         * @property {number} CHANNEL_LAYOUT_UNSPECIFIED=0 CHANNEL_LAYOUT_UNSPECIFIED value
         * @property {number} CHANNEL_LAYOUT_INTERLEAVED=1 CHANNEL_LAYOUT_INTERLEAVED value
         */
        v1.ChannelLayout = (function() {
            var valuesById = {}, values = Object.create(valuesById);
            values[valuesById[0] = "CHANNEL_LAYOUT_UNSPECIFIED"] = 0;
            values[valuesById[1] = "CHANNEL_LAYOUT_INTERLEAVED"] = 1;
            return values;
        })();

        v1.AudioFormat = (function() {

            /**
             * Properties of an AudioFormat.
             * @memberof fluent_audio.v1
             * @interface IAudioFormat
             * @property {number|null} [sampleRateHz] AudioFormat sampleRateHz
             * @property {number|null} [channels] AudioFormat channels
             * @property {fluent_audio.v1.SampleFormat|null} [sampleFormat] AudioFormat sampleFormat
             * @property {fluent_audio.v1.ChannelLayout|null} [channelLayout] AudioFormat channelLayout
             */

            /**
             * Constructs a new AudioFormat.
             * @memberof fluent_audio.v1
             * @classdesc Represents an AudioFormat.
             * @implements IAudioFormat
             * @constructor
             * @param {fluent_audio.v1.IAudioFormat=} [properties] Properties to set
             */
            function AudioFormat(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * AudioFormat sampleRateHz.
             * @member {number} sampleRateHz
             * @memberof fluent_audio.v1.AudioFormat
             * @instance
             */
            AudioFormat.prototype.sampleRateHz = 0;

            /**
             * AudioFormat channels.
             * @member {number} channels
             * @memberof fluent_audio.v1.AudioFormat
             * @instance
             */
            AudioFormat.prototype.channels = 0;

            /**
             * AudioFormat sampleFormat.
             * @member {fluent_audio.v1.SampleFormat} sampleFormat
             * @memberof fluent_audio.v1.AudioFormat
             * @instance
             */
            AudioFormat.prototype.sampleFormat = 0;

            /**
             * AudioFormat channelLayout.
             * @member {fluent_audio.v1.ChannelLayout} channelLayout
             * @memberof fluent_audio.v1.AudioFormat
             * @instance
             */
            AudioFormat.prototype.channelLayout = 0;

            /**
             * Creates a new AudioFormat instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.AudioFormat
             * @static
             * @param {fluent_audio.v1.IAudioFormat=} [properties] Properties to set
             * @returns {fluent_audio.v1.AudioFormat} AudioFormat instance
             */
            AudioFormat.create = function create(properties) {
                return new AudioFormat(properties);
            };

            /**
             * Encodes the specified AudioFormat message. Does not implicitly {@link fluent_audio.v1.AudioFormat.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.AudioFormat
             * @static
             * @param {fluent_audio.v1.IAudioFormat} message AudioFormat message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AudioFormat.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sampleRateHz != null && Object.hasOwnProperty.call(message, "sampleRateHz"))
                    writer.uint32(/* id 1, wireType 0 =*/8).uint32(message.sampleRateHz);
                if (message.channels != null && Object.hasOwnProperty.call(message, "channels"))
                    writer.uint32(/* id 2, wireType 0 =*/16).uint32(message.channels);
                if (message.sampleFormat != null && Object.hasOwnProperty.call(message, "sampleFormat"))
                    writer.uint32(/* id 3, wireType 0 =*/24).int32(message.sampleFormat);
                if (message.channelLayout != null && Object.hasOwnProperty.call(message, "channelLayout"))
                    writer.uint32(/* id 4, wireType 0 =*/32).int32(message.channelLayout);
                return writer;
            };

            /**
             * Encodes the specified AudioFormat message, length delimited. Does not implicitly {@link fluent_audio.v1.AudioFormat.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.AudioFormat
             * @static
             * @param {fluent_audio.v1.IAudioFormat} message AudioFormat message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AudioFormat.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes an AudioFormat message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.AudioFormat
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.AudioFormat} AudioFormat
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AudioFormat.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.AudioFormat();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sampleRateHz = reader.uint32();
                            break;
                        }
                    case 2: {
                            message.channels = reader.uint32();
                            break;
                        }
                    case 3: {
                            message.sampleFormat = reader.int32();
                            break;
                        }
                    case 4: {
                            message.channelLayout = reader.int32();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes an AudioFormat message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.AudioFormat
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.AudioFormat} AudioFormat
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AudioFormat.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies an AudioFormat message.
             * @function verify
             * @memberof fluent_audio.v1.AudioFormat
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            AudioFormat.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.sampleRateHz != null && Object.hasOwnProperty.call(message, "sampleRateHz"))
                    if (!$util.isInteger(message.sampleRateHz))
                        return "sampleRateHz: integer expected";
                if (message.channels != null && Object.hasOwnProperty.call(message, "channels"))
                    if (!$util.isInteger(message.channels))
                        return "channels: integer expected";
                if (message.sampleFormat != null && Object.hasOwnProperty.call(message, "sampleFormat"))
                    switch (message.sampleFormat) {
                    default:
                        return "sampleFormat: enum value expected";
                    case 0:
                    case 1:
                    case 2:
                        break;
                    }
                if (message.channelLayout != null && Object.hasOwnProperty.call(message, "channelLayout"))
                    switch (message.channelLayout) {
                    default:
                        return "channelLayout: enum value expected";
                    case 0:
                    case 1:
                        break;
                    }
                return null;
            };

            /**
             * Creates an AudioFormat message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.AudioFormat
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.AudioFormat} AudioFormat
             */
            AudioFormat.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.AudioFormat)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.AudioFormat: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.AudioFormat();
                if (object.sampleRateHz != null)
                    message.sampleRateHz = object.sampleRateHz >>> 0;
                if (object.channels != null)
                    message.channels = object.channels >>> 0;
                switch (object.sampleFormat) {
                default:
                    if (typeof object.sampleFormat === "number") {
                        message.sampleFormat = object.sampleFormat;
                        break;
                    }
                    break;
                case "SAMPLE_FORMAT_UNSPECIFIED":
                case 0:
                    message.sampleFormat = 0;
                    break;
                case "SAMPLE_FORMAT_S16LE":
                case 1:
                    message.sampleFormat = 1;
                    break;
                case "SAMPLE_FORMAT_F32LE":
                case 2:
                    message.sampleFormat = 2;
                    break;
                }
                switch (object.channelLayout) {
                default:
                    if (typeof object.channelLayout === "number") {
                        message.channelLayout = object.channelLayout;
                        break;
                    }
                    break;
                case "CHANNEL_LAYOUT_UNSPECIFIED":
                case 0:
                    message.channelLayout = 0;
                    break;
                case "CHANNEL_LAYOUT_INTERLEAVED":
                case 1:
                    message.channelLayout = 1;
                    break;
                }
                return message;
            };

            /**
             * Creates a plain object from an AudioFormat message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.AudioFormat
             * @static
             * @param {fluent_audio.v1.AudioFormat} message AudioFormat
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            AudioFormat.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.sampleRateHz = 0;
                    object.channels = 0;
                    object.sampleFormat = options.enums === String ? "SAMPLE_FORMAT_UNSPECIFIED" : 0;
                    object.channelLayout = options.enums === String ? "CHANNEL_LAYOUT_UNSPECIFIED" : 0;
                }
                if (message.sampleRateHz != null && Object.hasOwnProperty.call(message, "sampleRateHz"))
                    object.sampleRateHz = message.sampleRateHz;
                if (message.channels != null && Object.hasOwnProperty.call(message, "channels"))
                    object.channels = message.channels;
                if (message.sampleFormat != null && Object.hasOwnProperty.call(message, "sampleFormat"))
                    object.sampleFormat = options.enums === String ? $root.fluent_audio.v1.SampleFormat[message.sampleFormat] === undefined ? message.sampleFormat : $root.fluent_audio.v1.SampleFormat[message.sampleFormat] : message.sampleFormat;
                if (message.channelLayout != null && Object.hasOwnProperty.call(message, "channelLayout"))
                    object.channelLayout = options.enums === String ? $root.fluent_audio.v1.ChannelLayout[message.channelLayout] === undefined ? message.channelLayout : $root.fluent_audio.v1.ChannelLayout[message.channelLayout] : message.channelLayout;
                return object;
            };

            /**
             * Converts this AudioFormat to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.AudioFormat
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            AudioFormat.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for AudioFormat
             * @function getTypeUrl
             * @memberof fluent_audio.v1.AudioFormat
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            AudioFormat.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.AudioFormat";
            };

            return AudioFormat;
        })();

        v1.AudioFrame = (function() {

            /**
             * Properties of an AudioFrame.
             * @memberof fluent_audio.v1
             * @interface IAudioFrame
             * @property {string|null} [sourceId] AudioFrame sourceId
             * @property {string|null} [streamId] AudioFrame streamId
             * @property {number|Long|null} [seq] AudioFrame seq
             * @property {number|Long|null} [sampleIndex] AudioFrame sampleIndex
             * @property {number|Long|null} [captureTimeNs] AudioFrame captureTimeNs
             * @property {number|null} [frameCount] AudioFrame frameCount
             * @property {fluent_audio.v1.IAudioFormat|null} [format] AudioFrame format
             * @property {Uint8Array|null} [payload] AudioFrame payload
             */

            /**
             * Constructs a new AudioFrame.
             * @memberof fluent_audio.v1
             * @classdesc Represents an AudioFrame.
             * @implements IAudioFrame
             * @constructor
             * @param {fluent_audio.v1.IAudioFrame=} [properties] Properties to set
             */
            function AudioFrame(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * AudioFrame sourceId.
             * @member {string} sourceId
             * @memberof fluent_audio.v1.AudioFrame
             * @instance
             */
            AudioFrame.prototype.sourceId = "";

            /**
             * AudioFrame streamId.
             * @member {string} streamId
             * @memberof fluent_audio.v1.AudioFrame
             * @instance
             */
            AudioFrame.prototype.streamId = "";

            /**
             * AudioFrame seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.AudioFrame
             * @instance
             */
            AudioFrame.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * AudioFrame sampleIndex.
             * @member {number|Long} sampleIndex
             * @memberof fluent_audio.v1.AudioFrame
             * @instance
             */
            AudioFrame.prototype.sampleIndex = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * AudioFrame captureTimeNs.
             * @member {number|Long} captureTimeNs
             * @memberof fluent_audio.v1.AudioFrame
             * @instance
             */
            AudioFrame.prototype.captureTimeNs = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * AudioFrame frameCount.
             * @member {number} frameCount
             * @memberof fluent_audio.v1.AudioFrame
             * @instance
             */
            AudioFrame.prototype.frameCount = 0;

            /**
             * AudioFrame format.
             * @member {fluent_audio.v1.IAudioFormat|null|undefined} format
             * @memberof fluent_audio.v1.AudioFrame
             * @instance
             */
            AudioFrame.prototype.format = null;

            /**
             * AudioFrame payload.
             * @member {Uint8Array} payload
             * @memberof fluent_audio.v1.AudioFrame
             * @instance
             */
            AudioFrame.prototype.payload = $util.newBuffer([]);

            /**
             * Creates a new AudioFrame instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.AudioFrame
             * @static
             * @param {fluent_audio.v1.IAudioFrame=} [properties] Properties to set
             * @returns {fluent_audio.v1.AudioFrame} AudioFrame instance
             */
            AudioFrame.create = function create(properties) {
                return new AudioFrame(properties);
            };

            /**
             * Encodes the specified AudioFrame message. Does not implicitly {@link fluent_audio.v1.AudioFrame.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.AudioFrame
             * @static
             * @param {fluent_audio.v1.IAudioFrame} message AudioFrame message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AudioFrame.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sourceId != null && Object.hasOwnProperty.call(message, "sourceId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.sourceId);
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.streamId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 3, wireType 0 =*/24).uint64(message.seq);
                if (message.sampleIndex != null && Object.hasOwnProperty.call(message, "sampleIndex"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.sampleIndex);
                if (message.captureTimeNs != null && Object.hasOwnProperty.call(message, "captureTimeNs"))
                    writer.uint32(/* id 5, wireType 0 =*/40).uint64(message.captureTimeNs);
                if (message.frameCount != null && Object.hasOwnProperty.call(message, "frameCount"))
                    writer.uint32(/* id 6, wireType 0 =*/48).uint32(message.frameCount);
                if (message.format != null && Object.hasOwnProperty.call(message, "format"))
                    $root.fluent_audio.v1.AudioFormat.encode(message.format, writer.uint32(/* id 7, wireType 2 =*/58).fork(), q + 1).ldelim();
                if (message.payload != null && Object.hasOwnProperty.call(message, "payload"))
                    writer.uint32(/* id 8, wireType 2 =*/66).bytes(message.payload);
                return writer;
            };

            /**
             * Encodes the specified AudioFrame message, length delimited. Does not implicitly {@link fluent_audio.v1.AudioFrame.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.AudioFrame
             * @static
             * @param {fluent_audio.v1.IAudioFrame} message AudioFrame message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AudioFrame.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes an AudioFrame message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.AudioFrame
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.AudioFrame} AudioFrame
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AudioFrame.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.AudioFrame();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sourceId = reader.string();
                            break;
                        }
                    case 2: {
                            message.streamId = reader.string();
                            break;
                        }
                    case 3: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 4: {
                            message.sampleIndex = reader.uint64();
                            break;
                        }
                    case 5: {
                            message.captureTimeNs = reader.uint64();
                            break;
                        }
                    case 6: {
                            message.frameCount = reader.uint32();
                            break;
                        }
                    case 7: {
                            message.format = $root.fluent_audio.v1.AudioFormat.decode(reader, reader.uint32(), undefined, long + 1);
                            break;
                        }
                    case 8: {
                            message.payload = reader.bytes();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes an AudioFrame message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.AudioFrame
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.AudioFrame} AudioFrame
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AudioFrame.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies an AudioFrame message.
             * @function verify
             * @memberof fluent_audio.v1.AudioFrame
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            AudioFrame.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.sourceId != null && Object.hasOwnProperty.call(message, "sourceId"))
                    if (!$util.isString(message.sourceId))
                        return "sourceId: string expected";
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    if (!$util.isString(message.streamId))
                        return "streamId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.sampleIndex != null && Object.hasOwnProperty.call(message, "sampleIndex"))
                    if (!$util.isInteger(message.sampleIndex) && !(message.sampleIndex && $util.isInteger(message.sampleIndex.low) && $util.isInteger(message.sampleIndex.high)))
                        return "sampleIndex: integer|Long expected";
                if (message.captureTimeNs != null && Object.hasOwnProperty.call(message, "captureTimeNs"))
                    if (!$util.isInteger(message.captureTimeNs) && !(message.captureTimeNs && $util.isInteger(message.captureTimeNs.low) && $util.isInteger(message.captureTimeNs.high)))
                        return "captureTimeNs: integer|Long expected";
                if (message.frameCount != null && Object.hasOwnProperty.call(message, "frameCount"))
                    if (!$util.isInteger(message.frameCount))
                        return "frameCount: integer expected";
                if (message.format != null && Object.hasOwnProperty.call(message, "format")) {
                    var error = $root.fluent_audio.v1.AudioFormat.verify(message.format, long + 1);
                    if (error)
                        return "format." + error;
                }
                if (message.payload != null && Object.hasOwnProperty.call(message, "payload"))
                    if (!(message.payload && typeof message.payload.length === "number" || $util.isString(message.payload)))
                        return "payload: buffer expected";
                return null;
            };

            /**
             * Creates an AudioFrame message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.AudioFrame
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.AudioFrame} AudioFrame
             */
            AudioFrame.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.AudioFrame)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.AudioFrame: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.AudioFrame();
                if (object.sourceId != null)
                    message.sourceId = String(object.sourceId);
                if (object.streamId != null)
                    message.streamId = String(object.streamId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.sampleIndex != null)
                    if ($util.Long)
                        message.sampleIndex = $util.Long.fromValue(object.sampleIndex, true);
                    else if (typeof object.sampleIndex === "string")
                        message.sampleIndex = parseInt(object.sampleIndex, 10);
                    else if (typeof object.sampleIndex === "number")
                        message.sampleIndex = object.sampleIndex;
                    else if (typeof object.sampleIndex === "object")
                        message.sampleIndex = new $util.LongBits(object.sampleIndex.low >>> 0, object.sampleIndex.high >>> 0).toNumber(true);
                if (object.captureTimeNs != null)
                    if ($util.Long)
                        message.captureTimeNs = $util.Long.fromValue(object.captureTimeNs, true);
                    else if (typeof object.captureTimeNs === "string")
                        message.captureTimeNs = parseInt(object.captureTimeNs, 10);
                    else if (typeof object.captureTimeNs === "number")
                        message.captureTimeNs = object.captureTimeNs;
                    else if (typeof object.captureTimeNs === "object")
                        message.captureTimeNs = new $util.LongBits(object.captureTimeNs.low >>> 0, object.captureTimeNs.high >>> 0).toNumber(true);
                if (object.frameCount != null)
                    message.frameCount = object.frameCount >>> 0;
                if (object.format != null) {
                    if (!$util.isObject(object.format))
                        throw TypeError(".fluent_audio.v1.AudioFrame.format: object expected");
                    message.format = $root.fluent_audio.v1.AudioFormat.fromObject(object.format, long + 1);
                }
                if (object.payload != null)
                    if (typeof object.payload === "string")
                        $util.base64.decode(object.payload, message.payload = $util.newBuffer($util.base64.length(object.payload)), 0);
                    else if (object.payload.length >= 0)
                        message.payload = object.payload;
                return message;
            };

            /**
             * Creates a plain object from an AudioFrame message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.AudioFrame
             * @static
             * @param {fluent_audio.v1.AudioFrame} message AudioFrame
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            AudioFrame.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.sourceId = "";
                    object.streamId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.sampleIndex = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.sampleIndex = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.captureTimeNs = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.captureTimeNs = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    object.frameCount = 0;
                    object.format = null;
                    if (options.bytes === String)
                        object.payload = "";
                    else {
                        object.payload = [];
                        if (options.bytes !== Array)
                            object.payload = $util.newBuffer(object.payload);
                    }
                }
                if (message.sourceId != null && Object.hasOwnProperty.call(message, "sourceId"))
                    object.sourceId = message.sourceId;
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    object.streamId = message.streamId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.sampleIndex != null && Object.hasOwnProperty.call(message, "sampleIndex"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.sampleIndex = typeof message.sampleIndex === "number" ? BigInt(message.sampleIndex) : $util.Long.fromBits(message.sampleIndex.low >>> 0, message.sampleIndex.high >>> 0, true).toBigInt();
                    else if (typeof message.sampleIndex === "number")
                        object.sampleIndex = options.longs === String ? String(message.sampleIndex) : message.sampleIndex;
                    else
                        object.sampleIndex = options.longs === String ? $util.Long.prototype.toString.call(message.sampleIndex) : options.longs === Number ? new $util.LongBits(message.sampleIndex.low >>> 0, message.sampleIndex.high >>> 0).toNumber(true) : message.sampleIndex;
                if (message.captureTimeNs != null && Object.hasOwnProperty.call(message, "captureTimeNs"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.captureTimeNs = typeof message.captureTimeNs === "number" ? BigInt(message.captureTimeNs) : $util.Long.fromBits(message.captureTimeNs.low >>> 0, message.captureTimeNs.high >>> 0, true).toBigInt();
                    else if (typeof message.captureTimeNs === "number")
                        object.captureTimeNs = options.longs === String ? String(message.captureTimeNs) : message.captureTimeNs;
                    else
                        object.captureTimeNs = options.longs === String ? $util.Long.prototype.toString.call(message.captureTimeNs) : options.longs === Number ? new $util.LongBits(message.captureTimeNs.low >>> 0, message.captureTimeNs.high >>> 0).toNumber(true) : message.captureTimeNs;
                if (message.frameCount != null && Object.hasOwnProperty.call(message, "frameCount"))
                    object.frameCount = message.frameCount;
                if (message.format != null && Object.hasOwnProperty.call(message, "format"))
                    object.format = $root.fluent_audio.v1.AudioFormat.toObject(message.format, options, q + 1);
                if (message.payload != null && Object.hasOwnProperty.call(message, "payload"))
                    object.payload = options.bytes === String ? $util.base64.encode(message.payload, 0, message.payload.length) : options.bytes === Array ? Array.prototype.slice.call(message.payload) : message.payload;
                return object;
            };

            /**
             * Converts this AudioFrame to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.AudioFrame
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            AudioFrame.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for AudioFrame
             * @function getTypeUrl
             * @memberof fluent_audio.v1.AudioFrame
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            AudioFrame.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.AudioFrame";
            };

            return AudioFrame;
        })();

        v1.AudioStreamFinal = (function() {

            /**
             * Properties of an AudioStreamFinal.
             * @memberof fluent_audio.v1
             * @interface IAudioStreamFinal
             * @property {string|null} [sourceId] AudioStreamFinal sourceId
             * @property {string|null} [streamId] AudioStreamFinal streamId
             * @property {number|Long|null} [seq] AudioStreamFinal seq
             * @property {number|Long|null} [sampleIndex] AudioStreamFinal sampleIndex
             * @property {number|Long|null} [captureTimeNs] AudioStreamFinal captureTimeNs
             * @property {fluent_audio.v1.IAudioFormat|null} [format] AudioStreamFinal format
             */

            /**
             * Constructs a new AudioStreamFinal.
             * @memberof fluent_audio.v1
             * @classdesc Represents an AudioStreamFinal.
             * @implements IAudioStreamFinal
             * @constructor
             * @param {fluent_audio.v1.IAudioStreamFinal=} [properties] Properties to set
             */
            function AudioStreamFinal(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * AudioStreamFinal sourceId.
             * @member {string} sourceId
             * @memberof fluent_audio.v1.AudioStreamFinal
             * @instance
             */
            AudioStreamFinal.prototype.sourceId = "";

            /**
             * AudioStreamFinal streamId.
             * @member {string} streamId
             * @memberof fluent_audio.v1.AudioStreamFinal
             * @instance
             */
            AudioStreamFinal.prototype.streamId = "";

            /**
             * AudioStreamFinal seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.AudioStreamFinal
             * @instance
             */
            AudioStreamFinal.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * AudioStreamFinal sampleIndex.
             * @member {number|Long} sampleIndex
             * @memberof fluent_audio.v1.AudioStreamFinal
             * @instance
             */
            AudioStreamFinal.prototype.sampleIndex = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * AudioStreamFinal captureTimeNs.
             * @member {number|Long} captureTimeNs
             * @memberof fluent_audio.v1.AudioStreamFinal
             * @instance
             */
            AudioStreamFinal.prototype.captureTimeNs = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * AudioStreamFinal format.
             * @member {fluent_audio.v1.IAudioFormat|null|undefined} format
             * @memberof fluent_audio.v1.AudioStreamFinal
             * @instance
             */
            AudioStreamFinal.prototype.format = null;

            /**
             * Creates a new AudioStreamFinal instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.AudioStreamFinal
             * @static
             * @param {fluent_audio.v1.IAudioStreamFinal=} [properties] Properties to set
             * @returns {fluent_audio.v1.AudioStreamFinal} AudioStreamFinal instance
             */
            AudioStreamFinal.create = function create(properties) {
                return new AudioStreamFinal(properties);
            };

            /**
             * Encodes the specified AudioStreamFinal message. Does not implicitly {@link fluent_audio.v1.AudioStreamFinal.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.AudioStreamFinal
             * @static
             * @param {fluent_audio.v1.IAudioStreamFinal} message AudioStreamFinal message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AudioStreamFinal.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sourceId != null && Object.hasOwnProperty.call(message, "sourceId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.sourceId);
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.streamId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 3, wireType 0 =*/24).uint64(message.seq);
                if (message.sampleIndex != null && Object.hasOwnProperty.call(message, "sampleIndex"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.sampleIndex);
                if (message.captureTimeNs != null && Object.hasOwnProperty.call(message, "captureTimeNs"))
                    writer.uint32(/* id 5, wireType 0 =*/40).uint64(message.captureTimeNs);
                if (message.format != null && Object.hasOwnProperty.call(message, "format"))
                    $root.fluent_audio.v1.AudioFormat.encode(message.format, writer.uint32(/* id 6, wireType 2 =*/50).fork(), q + 1).ldelim();
                return writer;
            };

            /**
             * Encodes the specified AudioStreamFinal message, length delimited. Does not implicitly {@link fluent_audio.v1.AudioStreamFinal.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.AudioStreamFinal
             * @static
             * @param {fluent_audio.v1.IAudioStreamFinal} message AudioStreamFinal message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AudioStreamFinal.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes an AudioStreamFinal message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.AudioStreamFinal
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.AudioStreamFinal} AudioStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AudioStreamFinal.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.AudioStreamFinal();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sourceId = reader.string();
                            break;
                        }
                    case 2: {
                            message.streamId = reader.string();
                            break;
                        }
                    case 3: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 4: {
                            message.sampleIndex = reader.uint64();
                            break;
                        }
                    case 5: {
                            message.captureTimeNs = reader.uint64();
                            break;
                        }
                    case 6: {
                            message.format = $root.fluent_audio.v1.AudioFormat.decode(reader, reader.uint32(), undefined, long + 1);
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes an AudioStreamFinal message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.AudioStreamFinal
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.AudioStreamFinal} AudioStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AudioStreamFinal.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies an AudioStreamFinal message.
             * @function verify
             * @memberof fluent_audio.v1.AudioStreamFinal
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            AudioStreamFinal.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.sourceId != null && Object.hasOwnProperty.call(message, "sourceId"))
                    if (!$util.isString(message.sourceId))
                        return "sourceId: string expected";
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    if (!$util.isString(message.streamId))
                        return "streamId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.sampleIndex != null && Object.hasOwnProperty.call(message, "sampleIndex"))
                    if (!$util.isInteger(message.sampleIndex) && !(message.sampleIndex && $util.isInteger(message.sampleIndex.low) && $util.isInteger(message.sampleIndex.high)))
                        return "sampleIndex: integer|Long expected";
                if (message.captureTimeNs != null && Object.hasOwnProperty.call(message, "captureTimeNs"))
                    if (!$util.isInteger(message.captureTimeNs) && !(message.captureTimeNs && $util.isInteger(message.captureTimeNs.low) && $util.isInteger(message.captureTimeNs.high)))
                        return "captureTimeNs: integer|Long expected";
                if (message.format != null && Object.hasOwnProperty.call(message, "format")) {
                    var error = $root.fluent_audio.v1.AudioFormat.verify(message.format, long + 1);
                    if (error)
                        return "format." + error;
                }
                return null;
            };

            /**
             * Creates an AudioStreamFinal message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.AudioStreamFinal
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.AudioStreamFinal} AudioStreamFinal
             */
            AudioStreamFinal.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.AudioStreamFinal)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.AudioStreamFinal: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.AudioStreamFinal();
                if (object.sourceId != null)
                    message.sourceId = String(object.sourceId);
                if (object.streamId != null)
                    message.streamId = String(object.streamId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.sampleIndex != null)
                    if ($util.Long)
                        message.sampleIndex = $util.Long.fromValue(object.sampleIndex, true);
                    else if (typeof object.sampleIndex === "string")
                        message.sampleIndex = parseInt(object.sampleIndex, 10);
                    else if (typeof object.sampleIndex === "number")
                        message.sampleIndex = object.sampleIndex;
                    else if (typeof object.sampleIndex === "object")
                        message.sampleIndex = new $util.LongBits(object.sampleIndex.low >>> 0, object.sampleIndex.high >>> 0).toNumber(true);
                if (object.captureTimeNs != null)
                    if ($util.Long)
                        message.captureTimeNs = $util.Long.fromValue(object.captureTimeNs, true);
                    else if (typeof object.captureTimeNs === "string")
                        message.captureTimeNs = parseInt(object.captureTimeNs, 10);
                    else if (typeof object.captureTimeNs === "number")
                        message.captureTimeNs = object.captureTimeNs;
                    else if (typeof object.captureTimeNs === "object")
                        message.captureTimeNs = new $util.LongBits(object.captureTimeNs.low >>> 0, object.captureTimeNs.high >>> 0).toNumber(true);
                if (object.format != null) {
                    if (!$util.isObject(object.format))
                        throw TypeError(".fluent_audio.v1.AudioStreamFinal.format: object expected");
                    message.format = $root.fluent_audio.v1.AudioFormat.fromObject(object.format, long + 1);
                }
                return message;
            };

            /**
             * Creates a plain object from an AudioStreamFinal message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.AudioStreamFinal
             * @static
             * @param {fluent_audio.v1.AudioStreamFinal} message AudioStreamFinal
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            AudioStreamFinal.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.sourceId = "";
                    object.streamId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.sampleIndex = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.sampleIndex = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.captureTimeNs = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.captureTimeNs = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    object.format = null;
                }
                if (message.sourceId != null && Object.hasOwnProperty.call(message, "sourceId"))
                    object.sourceId = message.sourceId;
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    object.streamId = message.streamId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.sampleIndex != null && Object.hasOwnProperty.call(message, "sampleIndex"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.sampleIndex = typeof message.sampleIndex === "number" ? BigInt(message.sampleIndex) : $util.Long.fromBits(message.sampleIndex.low >>> 0, message.sampleIndex.high >>> 0, true).toBigInt();
                    else if (typeof message.sampleIndex === "number")
                        object.sampleIndex = options.longs === String ? String(message.sampleIndex) : message.sampleIndex;
                    else
                        object.sampleIndex = options.longs === String ? $util.Long.prototype.toString.call(message.sampleIndex) : options.longs === Number ? new $util.LongBits(message.sampleIndex.low >>> 0, message.sampleIndex.high >>> 0).toNumber(true) : message.sampleIndex;
                if (message.captureTimeNs != null && Object.hasOwnProperty.call(message, "captureTimeNs"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.captureTimeNs = typeof message.captureTimeNs === "number" ? BigInt(message.captureTimeNs) : $util.Long.fromBits(message.captureTimeNs.low >>> 0, message.captureTimeNs.high >>> 0, true).toBigInt();
                    else if (typeof message.captureTimeNs === "number")
                        object.captureTimeNs = options.longs === String ? String(message.captureTimeNs) : message.captureTimeNs;
                    else
                        object.captureTimeNs = options.longs === String ? $util.Long.prototype.toString.call(message.captureTimeNs) : options.longs === Number ? new $util.LongBits(message.captureTimeNs.low >>> 0, message.captureTimeNs.high >>> 0).toNumber(true) : message.captureTimeNs;
                if (message.format != null && Object.hasOwnProperty.call(message, "format"))
                    object.format = $root.fluent_audio.v1.AudioFormat.toObject(message.format, options, q + 1);
                return object;
            };

            /**
             * Converts this AudioStreamFinal to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.AudioStreamFinal
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            AudioStreamFinal.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for AudioStreamFinal
             * @function getTypeUrl
             * @memberof fluent_audio.v1.AudioStreamFinal
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            AudioStreamFinal.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.AudioStreamFinal";
            };

            return AudioStreamFinal;
        })();

        /**
         * VoiceActivityState enum.
         * @name fluent_audio.v1.VoiceActivityState
         * @enum {number}
         * @property {number} VOICE_ACTIVITY_STATE_UNSPECIFIED=0 VOICE_ACTIVITY_STATE_UNSPECIFIED value
         * @property {number} VOICE_ACTIVITY_STATE_SILENCE=1 VOICE_ACTIVITY_STATE_SILENCE value
         * @property {number} VOICE_ACTIVITY_STATE_SPEECH=2 VOICE_ACTIVITY_STATE_SPEECH value
         */
        v1.VoiceActivityState = (function() {
            var valuesById = {}, values = Object.create(valuesById);
            values[valuesById[0] = "VOICE_ACTIVITY_STATE_UNSPECIFIED"] = 0;
            values[valuesById[1] = "VOICE_ACTIVITY_STATE_SILENCE"] = 1;
            values[valuesById[2] = "VOICE_ACTIVITY_STATE_SPEECH"] = 2;
            return values;
        })();

        /**
         * TurnState enum.
         * @name fluent_audio.v1.TurnState
         * @enum {number}
         * @property {number} TURN_STATE_UNSPECIFIED=0 TURN_STATE_UNSPECIFIED value
         * @property {number} TURN_STATE_IDLE=1 TURN_STATE_IDLE value
         * @property {number} TURN_STATE_STARTED=2 TURN_STATE_STARTED value
         * @property {number} TURN_STATE_ACTIVE=3 TURN_STATE_ACTIVE value
         * @property {number} TURN_STATE_ENDED=4 TURN_STATE_ENDED value
         * @property {number} TURN_STATE_CANCELLED=5 TURN_STATE_CANCELLED value
         */
        v1.TurnState = (function() {
            var valuesById = {}, values = Object.create(valuesById);
            values[valuesById[0] = "TURN_STATE_UNSPECIFIED"] = 0;
            values[valuesById[1] = "TURN_STATE_IDLE"] = 1;
            values[valuesById[2] = "TURN_STATE_STARTED"] = 2;
            values[valuesById[3] = "TURN_STATE_ACTIVE"] = 3;
            values[valuesById[4] = "TURN_STATE_ENDED"] = 4;
            values[valuesById[5] = "TURN_STATE_CANCELLED"] = 5;
            return values;
        })();

        v1.VoiceActivityEvent = (function() {

            /**
             * Properties of a VoiceActivityEvent.
             * @memberof fluent_audio.v1
             * @interface IVoiceActivityEvent
             * @property {string|null} [sourceId] VoiceActivityEvent sourceId
             * @property {string|null} [streamId] VoiceActivityEvent streamId
             * @property {number|Long|null} [seq] VoiceActivityEvent seq
             * @property {number|Long|null} [sampleIndex] VoiceActivityEvent sampleIndex
             * @property {number|null} [frameCount] VoiceActivityEvent frameCount
             * @property {fluent_audio.v1.VoiceActivityState|null} [state] VoiceActivityEvent state
             * @property {number|null} [speechProbability] VoiceActivityEvent speechProbability
             */

            /**
             * Constructs a new VoiceActivityEvent.
             * @memberof fluent_audio.v1
             * @classdesc Represents a VoiceActivityEvent.
             * @implements IVoiceActivityEvent
             * @constructor
             * @param {fluent_audio.v1.IVoiceActivityEvent=} [properties] Properties to set
             */
            function VoiceActivityEvent(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * VoiceActivityEvent sourceId.
             * @member {string} sourceId
             * @memberof fluent_audio.v1.VoiceActivityEvent
             * @instance
             */
            VoiceActivityEvent.prototype.sourceId = "";

            /**
             * VoiceActivityEvent streamId.
             * @member {string} streamId
             * @memberof fluent_audio.v1.VoiceActivityEvent
             * @instance
             */
            VoiceActivityEvent.prototype.streamId = "";

            /**
             * VoiceActivityEvent seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.VoiceActivityEvent
             * @instance
             */
            VoiceActivityEvent.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * VoiceActivityEvent sampleIndex.
             * @member {number|Long} sampleIndex
             * @memberof fluent_audio.v1.VoiceActivityEvent
             * @instance
             */
            VoiceActivityEvent.prototype.sampleIndex = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * VoiceActivityEvent frameCount.
             * @member {number} frameCount
             * @memberof fluent_audio.v1.VoiceActivityEvent
             * @instance
             */
            VoiceActivityEvent.prototype.frameCount = 0;

            /**
             * VoiceActivityEvent state.
             * @member {fluent_audio.v1.VoiceActivityState} state
             * @memberof fluent_audio.v1.VoiceActivityEvent
             * @instance
             */
            VoiceActivityEvent.prototype.state = 0;

            /**
             * VoiceActivityEvent speechProbability.
             * @member {number} speechProbability
             * @memberof fluent_audio.v1.VoiceActivityEvent
             * @instance
             */
            VoiceActivityEvent.prototype.speechProbability = 0;

            /**
             * Creates a new VoiceActivityEvent instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.VoiceActivityEvent
             * @static
             * @param {fluent_audio.v1.IVoiceActivityEvent=} [properties] Properties to set
             * @returns {fluent_audio.v1.VoiceActivityEvent} VoiceActivityEvent instance
             */
            VoiceActivityEvent.create = function create(properties) {
                return new VoiceActivityEvent(properties);
            };

            /**
             * Encodes the specified VoiceActivityEvent message. Does not implicitly {@link fluent_audio.v1.VoiceActivityEvent.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.VoiceActivityEvent
             * @static
             * @param {fluent_audio.v1.IVoiceActivityEvent} message VoiceActivityEvent message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            VoiceActivityEvent.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sourceId != null && Object.hasOwnProperty.call(message, "sourceId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.sourceId);
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.streamId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 3, wireType 0 =*/24).uint64(message.seq);
                if (message.sampleIndex != null && Object.hasOwnProperty.call(message, "sampleIndex"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.sampleIndex);
                if (message.frameCount != null && Object.hasOwnProperty.call(message, "frameCount"))
                    writer.uint32(/* id 5, wireType 0 =*/40).uint32(message.frameCount);
                if (message.state != null && Object.hasOwnProperty.call(message, "state"))
                    writer.uint32(/* id 6, wireType 0 =*/48).int32(message.state);
                if (message.speechProbability != null && Object.hasOwnProperty.call(message, "speechProbability"))
                    writer.uint32(/* id 7, wireType 1 =*/57).double(message.speechProbability);
                return writer;
            };

            /**
             * Encodes the specified VoiceActivityEvent message, length delimited. Does not implicitly {@link fluent_audio.v1.VoiceActivityEvent.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.VoiceActivityEvent
             * @static
             * @param {fluent_audio.v1.IVoiceActivityEvent} message VoiceActivityEvent message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            VoiceActivityEvent.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes a VoiceActivityEvent message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.VoiceActivityEvent
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.VoiceActivityEvent} VoiceActivityEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            VoiceActivityEvent.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.VoiceActivityEvent();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sourceId = reader.string();
                            break;
                        }
                    case 2: {
                            message.streamId = reader.string();
                            break;
                        }
                    case 3: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 4: {
                            message.sampleIndex = reader.uint64();
                            break;
                        }
                    case 5: {
                            message.frameCount = reader.uint32();
                            break;
                        }
                    case 6: {
                            message.state = reader.int32();
                            break;
                        }
                    case 7: {
                            message.speechProbability = reader.double();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes a VoiceActivityEvent message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.VoiceActivityEvent
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.VoiceActivityEvent} VoiceActivityEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            VoiceActivityEvent.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a VoiceActivityEvent message.
             * @function verify
             * @memberof fluent_audio.v1.VoiceActivityEvent
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            VoiceActivityEvent.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.sourceId != null && Object.hasOwnProperty.call(message, "sourceId"))
                    if (!$util.isString(message.sourceId))
                        return "sourceId: string expected";
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    if (!$util.isString(message.streamId))
                        return "streamId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.sampleIndex != null && Object.hasOwnProperty.call(message, "sampleIndex"))
                    if (!$util.isInteger(message.sampleIndex) && !(message.sampleIndex && $util.isInteger(message.sampleIndex.low) && $util.isInteger(message.sampleIndex.high)))
                        return "sampleIndex: integer|Long expected";
                if (message.frameCount != null && Object.hasOwnProperty.call(message, "frameCount"))
                    if (!$util.isInteger(message.frameCount))
                        return "frameCount: integer expected";
                if (message.state != null && Object.hasOwnProperty.call(message, "state"))
                    switch (message.state) {
                    default:
                        return "state: enum value expected";
                    case 0:
                    case 1:
                    case 2:
                        break;
                    }
                if (message.speechProbability != null && Object.hasOwnProperty.call(message, "speechProbability"))
                    if (typeof message.speechProbability !== "number")
                        return "speechProbability: number expected";
                return null;
            };

            /**
             * Creates a VoiceActivityEvent message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.VoiceActivityEvent
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.VoiceActivityEvent} VoiceActivityEvent
             */
            VoiceActivityEvent.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.VoiceActivityEvent)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.VoiceActivityEvent: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.VoiceActivityEvent();
                if (object.sourceId != null)
                    message.sourceId = String(object.sourceId);
                if (object.streamId != null)
                    message.streamId = String(object.streamId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.sampleIndex != null)
                    if ($util.Long)
                        message.sampleIndex = $util.Long.fromValue(object.sampleIndex, true);
                    else if (typeof object.sampleIndex === "string")
                        message.sampleIndex = parseInt(object.sampleIndex, 10);
                    else if (typeof object.sampleIndex === "number")
                        message.sampleIndex = object.sampleIndex;
                    else if (typeof object.sampleIndex === "object")
                        message.sampleIndex = new $util.LongBits(object.sampleIndex.low >>> 0, object.sampleIndex.high >>> 0).toNumber(true);
                if (object.frameCount != null)
                    message.frameCount = object.frameCount >>> 0;
                switch (object.state) {
                default:
                    if (typeof object.state === "number") {
                        message.state = object.state;
                        break;
                    }
                    break;
                case "VOICE_ACTIVITY_STATE_UNSPECIFIED":
                case 0:
                    message.state = 0;
                    break;
                case "VOICE_ACTIVITY_STATE_SILENCE":
                case 1:
                    message.state = 1;
                    break;
                case "VOICE_ACTIVITY_STATE_SPEECH":
                case 2:
                    message.state = 2;
                    break;
                }
                if (object.speechProbability != null)
                    message.speechProbability = Number(object.speechProbability);
                return message;
            };

            /**
             * Creates a plain object from a VoiceActivityEvent message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.VoiceActivityEvent
             * @static
             * @param {fluent_audio.v1.VoiceActivityEvent} message VoiceActivityEvent
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            VoiceActivityEvent.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.sourceId = "";
                    object.streamId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.sampleIndex = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.sampleIndex = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    object.frameCount = 0;
                    object.state = options.enums === String ? "VOICE_ACTIVITY_STATE_UNSPECIFIED" : 0;
                    object.speechProbability = 0;
                }
                if (message.sourceId != null && Object.hasOwnProperty.call(message, "sourceId"))
                    object.sourceId = message.sourceId;
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    object.streamId = message.streamId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.sampleIndex != null && Object.hasOwnProperty.call(message, "sampleIndex"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.sampleIndex = typeof message.sampleIndex === "number" ? BigInt(message.sampleIndex) : $util.Long.fromBits(message.sampleIndex.low >>> 0, message.sampleIndex.high >>> 0, true).toBigInt();
                    else if (typeof message.sampleIndex === "number")
                        object.sampleIndex = options.longs === String ? String(message.sampleIndex) : message.sampleIndex;
                    else
                        object.sampleIndex = options.longs === String ? $util.Long.prototype.toString.call(message.sampleIndex) : options.longs === Number ? new $util.LongBits(message.sampleIndex.low >>> 0, message.sampleIndex.high >>> 0).toNumber(true) : message.sampleIndex;
                if (message.frameCount != null && Object.hasOwnProperty.call(message, "frameCount"))
                    object.frameCount = message.frameCount;
                if (message.state != null && Object.hasOwnProperty.call(message, "state"))
                    object.state = options.enums === String ? $root.fluent_audio.v1.VoiceActivityState[message.state] === undefined ? message.state : $root.fluent_audio.v1.VoiceActivityState[message.state] : message.state;
                if (message.speechProbability != null && Object.hasOwnProperty.call(message, "speechProbability"))
                    object.speechProbability = options.json && !isFinite(message.speechProbability) ? String(message.speechProbability) : message.speechProbability;
                return object;
            };

            /**
             * Converts this VoiceActivityEvent to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.VoiceActivityEvent
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            VoiceActivityEvent.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for VoiceActivityEvent
             * @function getTypeUrl
             * @memberof fluent_audio.v1.VoiceActivityEvent
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            VoiceActivityEvent.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.VoiceActivityEvent";
            };

            return VoiceActivityEvent;
        })();

        v1.AudioLevelEvent = (function() {

            /**
             * Properties of an AudioLevelEvent.
             * @memberof fluent_audio.v1
             * @interface IAudioLevelEvent
             * @property {string|null} [sourceId] AudioLevelEvent sourceId
             * @property {string|null} [streamId] AudioLevelEvent streamId
             * @property {number|Long|null} [seq] AudioLevelEvent seq
             * @property {number|Long|null} [sampleIndex] AudioLevelEvent sampleIndex
             * @property {number|null} [frameCount] AudioLevelEvent frameCount
             * @property {number|null} [rmsDbfs] AudioLevelEvent rmsDbfs
             * @property {number|null} [peakDbfs] AudioLevelEvent peakDbfs
             * @property {number|null} [speechProbability] AudioLevelEvent speechProbability
             */

            /**
             * Constructs a new AudioLevelEvent.
             * @memberof fluent_audio.v1
             * @classdesc Represents an AudioLevelEvent.
             * @implements IAudioLevelEvent
             * @constructor
             * @param {fluent_audio.v1.IAudioLevelEvent=} [properties] Properties to set
             */
            function AudioLevelEvent(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * AudioLevelEvent sourceId.
             * @member {string} sourceId
             * @memberof fluent_audio.v1.AudioLevelEvent
             * @instance
             */
            AudioLevelEvent.prototype.sourceId = "";

            /**
             * AudioLevelEvent streamId.
             * @member {string} streamId
             * @memberof fluent_audio.v1.AudioLevelEvent
             * @instance
             */
            AudioLevelEvent.prototype.streamId = "";

            /**
             * AudioLevelEvent seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.AudioLevelEvent
             * @instance
             */
            AudioLevelEvent.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * AudioLevelEvent sampleIndex.
             * @member {number|Long} sampleIndex
             * @memberof fluent_audio.v1.AudioLevelEvent
             * @instance
             */
            AudioLevelEvent.prototype.sampleIndex = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * AudioLevelEvent frameCount.
             * @member {number} frameCount
             * @memberof fluent_audio.v1.AudioLevelEvent
             * @instance
             */
            AudioLevelEvent.prototype.frameCount = 0;

            /**
             * AudioLevelEvent rmsDbfs.
             * @member {number} rmsDbfs
             * @memberof fluent_audio.v1.AudioLevelEvent
             * @instance
             */
            AudioLevelEvent.prototype.rmsDbfs = 0;

            /**
             * AudioLevelEvent peakDbfs.
             * @member {number} peakDbfs
             * @memberof fluent_audio.v1.AudioLevelEvent
             * @instance
             */
            AudioLevelEvent.prototype.peakDbfs = 0;

            /**
             * AudioLevelEvent speechProbability.
             * @member {number} speechProbability
             * @memberof fluent_audio.v1.AudioLevelEvent
             * @instance
             */
            AudioLevelEvent.prototype.speechProbability = 0;

            /**
             * Creates a new AudioLevelEvent instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.AudioLevelEvent
             * @static
             * @param {fluent_audio.v1.IAudioLevelEvent=} [properties] Properties to set
             * @returns {fluent_audio.v1.AudioLevelEvent} AudioLevelEvent instance
             */
            AudioLevelEvent.create = function create(properties) {
                return new AudioLevelEvent(properties);
            };

            /**
             * Encodes the specified AudioLevelEvent message. Does not implicitly {@link fluent_audio.v1.AudioLevelEvent.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.AudioLevelEvent
             * @static
             * @param {fluent_audio.v1.IAudioLevelEvent} message AudioLevelEvent message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AudioLevelEvent.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sourceId != null && Object.hasOwnProperty.call(message, "sourceId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.sourceId);
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.streamId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 3, wireType 0 =*/24).uint64(message.seq);
                if (message.sampleIndex != null && Object.hasOwnProperty.call(message, "sampleIndex"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.sampleIndex);
                if (message.frameCount != null && Object.hasOwnProperty.call(message, "frameCount"))
                    writer.uint32(/* id 5, wireType 0 =*/40).uint32(message.frameCount);
                if (message.rmsDbfs != null && Object.hasOwnProperty.call(message, "rmsDbfs"))
                    writer.uint32(/* id 6, wireType 1 =*/49).double(message.rmsDbfs);
                if (message.peakDbfs != null && Object.hasOwnProperty.call(message, "peakDbfs"))
                    writer.uint32(/* id 7, wireType 1 =*/57).double(message.peakDbfs);
                if (message.speechProbability != null && Object.hasOwnProperty.call(message, "speechProbability"))
                    writer.uint32(/* id 8, wireType 1 =*/65).double(message.speechProbability);
                return writer;
            };

            /**
             * Encodes the specified AudioLevelEvent message, length delimited. Does not implicitly {@link fluent_audio.v1.AudioLevelEvent.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.AudioLevelEvent
             * @static
             * @param {fluent_audio.v1.IAudioLevelEvent} message AudioLevelEvent message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AudioLevelEvent.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes an AudioLevelEvent message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.AudioLevelEvent
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.AudioLevelEvent} AudioLevelEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AudioLevelEvent.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.AudioLevelEvent();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sourceId = reader.string();
                            break;
                        }
                    case 2: {
                            message.streamId = reader.string();
                            break;
                        }
                    case 3: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 4: {
                            message.sampleIndex = reader.uint64();
                            break;
                        }
                    case 5: {
                            message.frameCount = reader.uint32();
                            break;
                        }
                    case 6: {
                            message.rmsDbfs = reader.double();
                            break;
                        }
                    case 7: {
                            message.peakDbfs = reader.double();
                            break;
                        }
                    case 8: {
                            message.speechProbability = reader.double();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes an AudioLevelEvent message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.AudioLevelEvent
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.AudioLevelEvent} AudioLevelEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AudioLevelEvent.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies an AudioLevelEvent message.
             * @function verify
             * @memberof fluent_audio.v1.AudioLevelEvent
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            AudioLevelEvent.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.sourceId != null && Object.hasOwnProperty.call(message, "sourceId"))
                    if (!$util.isString(message.sourceId))
                        return "sourceId: string expected";
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    if (!$util.isString(message.streamId))
                        return "streamId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.sampleIndex != null && Object.hasOwnProperty.call(message, "sampleIndex"))
                    if (!$util.isInteger(message.sampleIndex) && !(message.sampleIndex && $util.isInteger(message.sampleIndex.low) && $util.isInteger(message.sampleIndex.high)))
                        return "sampleIndex: integer|Long expected";
                if (message.frameCount != null && Object.hasOwnProperty.call(message, "frameCount"))
                    if (!$util.isInteger(message.frameCount))
                        return "frameCount: integer expected";
                if (message.rmsDbfs != null && Object.hasOwnProperty.call(message, "rmsDbfs"))
                    if (typeof message.rmsDbfs !== "number")
                        return "rmsDbfs: number expected";
                if (message.peakDbfs != null && Object.hasOwnProperty.call(message, "peakDbfs"))
                    if (typeof message.peakDbfs !== "number")
                        return "peakDbfs: number expected";
                if (message.speechProbability != null && Object.hasOwnProperty.call(message, "speechProbability"))
                    if (typeof message.speechProbability !== "number")
                        return "speechProbability: number expected";
                return null;
            };

            /**
             * Creates an AudioLevelEvent message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.AudioLevelEvent
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.AudioLevelEvent} AudioLevelEvent
             */
            AudioLevelEvent.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.AudioLevelEvent)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.AudioLevelEvent: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.AudioLevelEvent();
                if (object.sourceId != null)
                    message.sourceId = String(object.sourceId);
                if (object.streamId != null)
                    message.streamId = String(object.streamId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.sampleIndex != null)
                    if ($util.Long)
                        message.sampleIndex = $util.Long.fromValue(object.sampleIndex, true);
                    else if (typeof object.sampleIndex === "string")
                        message.sampleIndex = parseInt(object.sampleIndex, 10);
                    else if (typeof object.sampleIndex === "number")
                        message.sampleIndex = object.sampleIndex;
                    else if (typeof object.sampleIndex === "object")
                        message.sampleIndex = new $util.LongBits(object.sampleIndex.low >>> 0, object.sampleIndex.high >>> 0).toNumber(true);
                if (object.frameCount != null)
                    message.frameCount = object.frameCount >>> 0;
                if (object.rmsDbfs != null)
                    message.rmsDbfs = Number(object.rmsDbfs);
                if (object.peakDbfs != null)
                    message.peakDbfs = Number(object.peakDbfs);
                if (object.speechProbability != null)
                    message.speechProbability = Number(object.speechProbability);
                return message;
            };

            /**
             * Creates a plain object from an AudioLevelEvent message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.AudioLevelEvent
             * @static
             * @param {fluent_audio.v1.AudioLevelEvent} message AudioLevelEvent
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            AudioLevelEvent.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.sourceId = "";
                    object.streamId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.sampleIndex = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.sampleIndex = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    object.frameCount = 0;
                    object.rmsDbfs = 0;
                    object.peakDbfs = 0;
                    object.speechProbability = 0;
                }
                if (message.sourceId != null && Object.hasOwnProperty.call(message, "sourceId"))
                    object.sourceId = message.sourceId;
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    object.streamId = message.streamId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.sampleIndex != null && Object.hasOwnProperty.call(message, "sampleIndex"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.sampleIndex = typeof message.sampleIndex === "number" ? BigInt(message.sampleIndex) : $util.Long.fromBits(message.sampleIndex.low >>> 0, message.sampleIndex.high >>> 0, true).toBigInt();
                    else if (typeof message.sampleIndex === "number")
                        object.sampleIndex = options.longs === String ? String(message.sampleIndex) : message.sampleIndex;
                    else
                        object.sampleIndex = options.longs === String ? $util.Long.prototype.toString.call(message.sampleIndex) : options.longs === Number ? new $util.LongBits(message.sampleIndex.low >>> 0, message.sampleIndex.high >>> 0).toNumber(true) : message.sampleIndex;
                if (message.frameCount != null && Object.hasOwnProperty.call(message, "frameCount"))
                    object.frameCount = message.frameCount;
                if (message.rmsDbfs != null && Object.hasOwnProperty.call(message, "rmsDbfs"))
                    object.rmsDbfs = options.json && !isFinite(message.rmsDbfs) ? String(message.rmsDbfs) : message.rmsDbfs;
                if (message.peakDbfs != null && Object.hasOwnProperty.call(message, "peakDbfs"))
                    object.peakDbfs = options.json && !isFinite(message.peakDbfs) ? String(message.peakDbfs) : message.peakDbfs;
                if (message.speechProbability != null && Object.hasOwnProperty.call(message, "speechProbability"))
                    object.speechProbability = options.json && !isFinite(message.speechProbability) ? String(message.speechProbability) : message.speechProbability;
                return object;
            };

            /**
             * Converts this AudioLevelEvent to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.AudioLevelEvent
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            AudioLevelEvent.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for AudioLevelEvent
             * @function getTypeUrl
             * @memberof fluent_audio.v1.AudioLevelEvent
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            AudioLevelEvent.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.AudioLevelEvent";
            };

            return AudioLevelEvent;
        })();

        v1.VoiceActivityStreamFinal = (function() {

            /**
             * Properties of a VoiceActivityStreamFinal.
             * @memberof fluent_audio.v1
             * @interface IVoiceActivityStreamFinal
             * @property {string|null} [sourceId] VoiceActivityStreamFinal sourceId
             * @property {string|null} [streamId] VoiceActivityStreamFinal streamId
             * @property {number|Long|null} [seq] VoiceActivityStreamFinal seq
             * @property {number|Long|null} [sampleIndex] VoiceActivityStreamFinal sampleIndex
             */

            /**
             * Constructs a new VoiceActivityStreamFinal.
             * @memberof fluent_audio.v1
             * @classdesc Represents a VoiceActivityStreamFinal.
             * @implements IVoiceActivityStreamFinal
             * @constructor
             * @param {fluent_audio.v1.IVoiceActivityStreamFinal=} [properties] Properties to set
             */
            function VoiceActivityStreamFinal(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * VoiceActivityStreamFinal sourceId.
             * @member {string} sourceId
             * @memberof fluent_audio.v1.VoiceActivityStreamFinal
             * @instance
             */
            VoiceActivityStreamFinal.prototype.sourceId = "";

            /**
             * VoiceActivityStreamFinal streamId.
             * @member {string} streamId
             * @memberof fluent_audio.v1.VoiceActivityStreamFinal
             * @instance
             */
            VoiceActivityStreamFinal.prototype.streamId = "";

            /**
             * VoiceActivityStreamFinal seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.VoiceActivityStreamFinal
             * @instance
             */
            VoiceActivityStreamFinal.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * VoiceActivityStreamFinal sampleIndex.
             * @member {number|Long} sampleIndex
             * @memberof fluent_audio.v1.VoiceActivityStreamFinal
             * @instance
             */
            VoiceActivityStreamFinal.prototype.sampleIndex = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * Creates a new VoiceActivityStreamFinal instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.VoiceActivityStreamFinal
             * @static
             * @param {fluent_audio.v1.IVoiceActivityStreamFinal=} [properties] Properties to set
             * @returns {fluent_audio.v1.VoiceActivityStreamFinal} VoiceActivityStreamFinal instance
             */
            VoiceActivityStreamFinal.create = function create(properties) {
                return new VoiceActivityStreamFinal(properties);
            };

            /**
             * Encodes the specified VoiceActivityStreamFinal message. Does not implicitly {@link fluent_audio.v1.VoiceActivityStreamFinal.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.VoiceActivityStreamFinal
             * @static
             * @param {fluent_audio.v1.IVoiceActivityStreamFinal} message VoiceActivityStreamFinal message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            VoiceActivityStreamFinal.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sourceId != null && Object.hasOwnProperty.call(message, "sourceId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.sourceId);
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.streamId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 3, wireType 0 =*/24).uint64(message.seq);
                if (message.sampleIndex != null && Object.hasOwnProperty.call(message, "sampleIndex"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.sampleIndex);
                return writer;
            };

            /**
             * Encodes the specified VoiceActivityStreamFinal message, length delimited. Does not implicitly {@link fluent_audio.v1.VoiceActivityStreamFinal.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.VoiceActivityStreamFinal
             * @static
             * @param {fluent_audio.v1.IVoiceActivityStreamFinal} message VoiceActivityStreamFinal message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            VoiceActivityStreamFinal.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes a VoiceActivityStreamFinal message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.VoiceActivityStreamFinal
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.VoiceActivityStreamFinal} VoiceActivityStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            VoiceActivityStreamFinal.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.VoiceActivityStreamFinal();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sourceId = reader.string();
                            break;
                        }
                    case 2: {
                            message.streamId = reader.string();
                            break;
                        }
                    case 3: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 4: {
                            message.sampleIndex = reader.uint64();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes a VoiceActivityStreamFinal message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.VoiceActivityStreamFinal
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.VoiceActivityStreamFinal} VoiceActivityStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            VoiceActivityStreamFinal.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a VoiceActivityStreamFinal message.
             * @function verify
             * @memberof fluent_audio.v1.VoiceActivityStreamFinal
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            VoiceActivityStreamFinal.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.sourceId != null && Object.hasOwnProperty.call(message, "sourceId"))
                    if (!$util.isString(message.sourceId))
                        return "sourceId: string expected";
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    if (!$util.isString(message.streamId))
                        return "streamId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.sampleIndex != null && Object.hasOwnProperty.call(message, "sampleIndex"))
                    if (!$util.isInteger(message.sampleIndex) && !(message.sampleIndex && $util.isInteger(message.sampleIndex.low) && $util.isInteger(message.sampleIndex.high)))
                        return "sampleIndex: integer|Long expected";
                return null;
            };

            /**
             * Creates a VoiceActivityStreamFinal message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.VoiceActivityStreamFinal
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.VoiceActivityStreamFinal} VoiceActivityStreamFinal
             */
            VoiceActivityStreamFinal.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.VoiceActivityStreamFinal)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.VoiceActivityStreamFinal: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.VoiceActivityStreamFinal();
                if (object.sourceId != null)
                    message.sourceId = String(object.sourceId);
                if (object.streamId != null)
                    message.streamId = String(object.streamId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.sampleIndex != null)
                    if ($util.Long)
                        message.sampleIndex = $util.Long.fromValue(object.sampleIndex, true);
                    else if (typeof object.sampleIndex === "string")
                        message.sampleIndex = parseInt(object.sampleIndex, 10);
                    else if (typeof object.sampleIndex === "number")
                        message.sampleIndex = object.sampleIndex;
                    else if (typeof object.sampleIndex === "object")
                        message.sampleIndex = new $util.LongBits(object.sampleIndex.low >>> 0, object.sampleIndex.high >>> 0).toNumber(true);
                return message;
            };

            /**
             * Creates a plain object from a VoiceActivityStreamFinal message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.VoiceActivityStreamFinal
             * @static
             * @param {fluent_audio.v1.VoiceActivityStreamFinal} message VoiceActivityStreamFinal
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            VoiceActivityStreamFinal.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.sourceId = "";
                    object.streamId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.sampleIndex = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.sampleIndex = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                }
                if (message.sourceId != null && Object.hasOwnProperty.call(message, "sourceId"))
                    object.sourceId = message.sourceId;
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    object.streamId = message.streamId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.sampleIndex != null && Object.hasOwnProperty.call(message, "sampleIndex"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.sampleIndex = typeof message.sampleIndex === "number" ? BigInt(message.sampleIndex) : $util.Long.fromBits(message.sampleIndex.low >>> 0, message.sampleIndex.high >>> 0, true).toBigInt();
                    else if (typeof message.sampleIndex === "number")
                        object.sampleIndex = options.longs === String ? String(message.sampleIndex) : message.sampleIndex;
                    else
                        object.sampleIndex = options.longs === String ? $util.Long.prototype.toString.call(message.sampleIndex) : options.longs === Number ? new $util.LongBits(message.sampleIndex.low >>> 0, message.sampleIndex.high >>> 0).toNumber(true) : message.sampleIndex;
                return object;
            };

            /**
             * Converts this VoiceActivityStreamFinal to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.VoiceActivityStreamFinal
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            VoiceActivityStreamFinal.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for VoiceActivityStreamFinal
             * @function getTypeUrl
             * @memberof fluent_audio.v1.VoiceActivityStreamFinal
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            VoiceActivityStreamFinal.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.VoiceActivityStreamFinal";
            };

            return VoiceActivityStreamFinal;
        })();

        v1.TurnEvent = (function() {

            /**
             * Properties of a TurnEvent.
             * @memberof fluent_audio.v1
             * @interface ITurnEvent
             * @property {string|null} [sessionId] TurnEvent sessionId
             * @property {string|null} [userTurnId] TurnEvent userTurnId
             * @property {string|null} [streamId] TurnEvent streamId
             * @property {number|Long|null} [seq] TurnEvent seq
             * @property {number|Long|null} [sampleIndex] TurnEvent sampleIndex
             * @property {fluent_audio.v1.TurnState|null} [state] TurnEvent state
             * @property {number|null} [confidence] TurnEvent confidence
             */

            /**
             * Constructs a new TurnEvent.
             * @memberof fluent_audio.v1
             * @classdesc Represents a TurnEvent.
             * @implements ITurnEvent
             * @constructor
             * @param {fluent_audio.v1.ITurnEvent=} [properties] Properties to set
             */
            function TurnEvent(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * TurnEvent sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.TurnEvent
             * @instance
             */
            TurnEvent.prototype.sessionId = "";

            /**
             * TurnEvent userTurnId.
             * @member {string} userTurnId
             * @memberof fluent_audio.v1.TurnEvent
             * @instance
             */
            TurnEvent.prototype.userTurnId = "";

            /**
             * TurnEvent streamId.
             * @member {string} streamId
             * @memberof fluent_audio.v1.TurnEvent
             * @instance
             */
            TurnEvent.prototype.streamId = "";

            /**
             * TurnEvent seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.TurnEvent
             * @instance
             */
            TurnEvent.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * TurnEvent sampleIndex.
             * @member {number|Long} sampleIndex
             * @memberof fluent_audio.v1.TurnEvent
             * @instance
             */
            TurnEvent.prototype.sampleIndex = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * TurnEvent state.
             * @member {fluent_audio.v1.TurnState} state
             * @memberof fluent_audio.v1.TurnEvent
             * @instance
             */
            TurnEvent.prototype.state = 0;

            /**
             * TurnEvent confidence.
             * @member {number|null|undefined} confidence
             * @memberof fluent_audio.v1.TurnEvent
             * @instance
             */
            TurnEvent.prototype.confidence = null;

            // OneOf field names bound to virtual getters and setters
            var $oneOfFields;

            // Virtual OneOf for proto3 optional field
            Object.defineProperty(TurnEvent.prototype, "_confidence", {
                get: $util.oneOfGetter($oneOfFields = ["confidence"]),
                set: $util.oneOfSetter($oneOfFields)
            });

            /**
             * Creates a new TurnEvent instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.TurnEvent
             * @static
             * @param {fluent_audio.v1.ITurnEvent=} [properties] Properties to set
             * @returns {fluent_audio.v1.TurnEvent} TurnEvent instance
             */
            TurnEvent.create = function create(properties) {
                return new TurnEvent(properties);
            };

            /**
             * Encodes the specified TurnEvent message. Does not implicitly {@link fluent_audio.v1.TurnEvent.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.TurnEvent
             * @static
             * @param {fluent_audio.v1.ITurnEvent} message TurnEvent message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            TurnEvent.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.sessionId);
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.userTurnId);
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.streamId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.seq);
                if (message.sampleIndex != null && Object.hasOwnProperty.call(message, "sampleIndex"))
                    writer.uint32(/* id 5, wireType 0 =*/40).uint64(message.sampleIndex);
                if (message.state != null && Object.hasOwnProperty.call(message, "state"))
                    writer.uint32(/* id 6, wireType 0 =*/48).int32(message.state);
                if (message.confidence != null && Object.hasOwnProperty.call(message, "confidence"))
                    writer.uint32(/* id 7, wireType 1 =*/57).double(message.confidence);
                return writer;
            };

            /**
             * Encodes the specified TurnEvent message, length delimited. Does not implicitly {@link fluent_audio.v1.TurnEvent.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.TurnEvent
             * @static
             * @param {fluent_audio.v1.ITurnEvent} message TurnEvent message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            TurnEvent.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes a TurnEvent message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.TurnEvent
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.TurnEvent} TurnEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            TurnEvent.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.TurnEvent();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 2: {
                            message.userTurnId = reader.string();
                            break;
                        }
                    case 3: {
                            message.streamId = reader.string();
                            break;
                        }
                    case 4: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 5: {
                            message.sampleIndex = reader.uint64();
                            break;
                        }
                    case 6: {
                            message.state = reader.int32();
                            break;
                        }
                    case 7: {
                            message.confidence = reader.double();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes a TurnEvent message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.TurnEvent
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.TurnEvent} TurnEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            TurnEvent.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a TurnEvent message.
             * @function verify
             * @memberof fluent_audio.v1.TurnEvent
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            TurnEvent.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                var properties = {};
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    if (!$util.isString(message.userTurnId))
                        return "userTurnId: string expected";
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    if (!$util.isString(message.streamId))
                        return "streamId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.sampleIndex != null && Object.hasOwnProperty.call(message, "sampleIndex"))
                    if (!$util.isInteger(message.sampleIndex) && !(message.sampleIndex && $util.isInteger(message.sampleIndex.low) && $util.isInteger(message.sampleIndex.high)))
                        return "sampleIndex: integer|Long expected";
                if (message.state != null && Object.hasOwnProperty.call(message, "state"))
                    switch (message.state) {
                    default:
                        return "state: enum value expected";
                    case 0:
                    case 1:
                    case 2:
                    case 3:
                    case 4:
                    case 5:
                        break;
                    }
                if (message.confidence != null && Object.hasOwnProperty.call(message, "confidence")) {
                    properties._confidence = 1;
                    if (typeof message.confidence !== "number")
                        return "confidence: number expected";
                }
                return null;
            };

            /**
             * Creates a TurnEvent message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.TurnEvent
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.TurnEvent} TurnEvent
             */
            TurnEvent.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.TurnEvent)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.TurnEvent: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.TurnEvent();
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.userTurnId != null)
                    message.userTurnId = String(object.userTurnId);
                if (object.streamId != null)
                    message.streamId = String(object.streamId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.sampleIndex != null)
                    if ($util.Long)
                        message.sampleIndex = $util.Long.fromValue(object.sampleIndex, true);
                    else if (typeof object.sampleIndex === "string")
                        message.sampleIndex = parseInt(object.sampleIndex, 10);
                    else if (typeof object.sampleIndex === "number")
                        message.sampleIndex = object.sampleIndex;
                    else if (typeof object.sampleIndex === "object")
                        message.sampleIndex = new $util.LongBits(object.sampleIndex.low >>> 0, object.sampleIndex.high >>> 0).toNumber(true);
                switch (object.state) {
                default:
                    if (typeof object.state === "number") {
                        message.state = object.state;
                        break;
                    }
                    break;
                case "TURN_STATE_UNSPECIFIED":
                case 0:
                    message.state = 0;
                    break;
                case "TURN_STATE_IDLE":
                case 1:
                    message.state = 1;
                    break;
                case "TURN_STATE_STARTED":
                case 2:
                    message.state = 2;
                    break;
                case "TURN_STATE_ACTIVE":
                case 3:
                    message.state = 3;
                    break;
                case "TURN_STATE_ENDED":
                case 4:
                    message.state = 4;
                    break;
                case "TURN_STATE_CANCELLED":
                case 5:
                    message.state = 5;
                    break;
                }
                if (object.confidence != null)
                    message.confidence = Number(object.confidence);
                return message;
            };

            /**
             * Creates a plain object from a TurnEvent message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.TurnEvent
             * @static
             * @param {fluent_audio.v1.TurnEvent} message TurnEvent
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            TurnEvent.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.sessionId = "";
                    object.userTurnId = "";
                    object.streamId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.sampleIndex = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.sampleIndex = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    object.state = options.enums === String ? "TURN_STATE_UNSPECIFIED" : 0;
                }
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    object.userTurnId = message.userTurnId;
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    object.streamId = message.streamId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.sampleIndex != null && Object.hasOwnProperty.call(message, "sampleIndex"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.sampleIndex = typeof message.sampleIndex === "number" ? BigInt(message.sampleIndex) : $util.Long.fromBits(message.sampleIndex.low >>> 0, message.sampleIndex.high >>> 0, true).toBigInt();
                    else if (typeof message.sampleIndex === "number")
                        object.sampleIndex = options.longs === String ? String(message.sampleIndex) : message.sampleIndex;
                    else
                        object.sampleIndex = options.longs === String ? $util.Long.prototype.toString.call(message.sampleIndex) : options.longs === Number ? new $util.LongBits(message.sampleIndex.low >>> 0, message.sampleIndex.high >>> 0).toNumber(true) : message.sampleIndex;
                if (message.state != null && Object.hasOwnProperty.call(message, "state"))
                    object.state = options.enums === String ? $root.fluent_audio.v1.TurnState[message.state] === undefined ? message.state : $root.fluent_audio.v1.TurnState[message.state] : message.state;
                if (message.confidence != null && Object.hasOwnProperty.call(message, "confidence")) {
                    object.confidence = options.json && !isFinite(message.confidence) ? String(message.confidence) : message.confidence;
                    if (options.oneofs)
                        object._confidence = "confidence";
                }
                return object;
            };

            /**
             * Converts this TurnEvent to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.TurnEvent
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            TurnEvent.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for TurnEvent
             * @function getTypeUrl
             * @memberof fluent_audio.v1.TurnEvent
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            TurnEvent.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.TurnEvent";
            };

            return TurnEvent;
        })();

        v1.TurnStreamFinal = (function() {

            /**
             * Properties of a TurnStreamFinal.
             * @memberof fluent_audio.v1
             * @interface ITurnStreamFinal
             * @property {string|null} [sessionId] TurnStreamFinal sessionId
             * @property {string|null} [streamId] TurnStreamFinal streamId
             * @property {number|Long|null} [seq] TurnStreamFinal seq
             * @property {number|Long|null} [sampleIndex] TurnStreamFinal sampleIndex
             */

            /**
             * Constructs a new TurnStreamFinal.
             * @memberof fluent_audio.v1
             * @classdesc Represents a TurnStreamFinal.
             * @implements ITurnStreamFinal
             * @constructor
             * @param {fluent_audio.v1.ITurnStreamFinal=} [properties] Properties to set
             */
            function TurnStreamFinal(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * TurnStreamFinal sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.TurnStreamFinal
             * @instance
             */
            TurnStreamFinal.prototype.sessionId = "";

            /**
             * TurnStreamFinal streamId.
             * @member {string} streamId
             * @memberof fluent_audio.v1.TurnStreamFinal
             * @instance
             */
            TurnStreamFinal.prototype.streamId = "";

            /**
             * TurnStreamFinal seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.TurnStreamFinal
             * @instance
             */
            TurnStreamFinal.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * TurnStreamFinal sampleIndex.
             * @member {number|Long} sampleIndex
             * @memberof fluent_audio.v1.TurnStreamFinal
             * @instance
             */
            TurnStreamFinal.prototype.sampleIndex = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * Creates a new TurnStreamFinal instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.TurnStreamFinal
             * @static
             * @param {fluent_audio.v1.ITurnStreamFinal=} [properties] Properties to set
             * @returns {fluent_audio.v1.TurnStreamFinal} TurnStreamFinal instance
             */
            TurnStreamFinal.create = function create(properties) {
                return new TurnStreamFinal(properties);
            };

            /**
             * Encodes the specified TurnStreamFinal message. Does not implicitly {@link fluent_audio.v1.TurnStreamFinal.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.TurnStreamFinal
             * @static
             * @param {fluent_audio.v1.ITurnStreamFinal} message TurnStreamFinal message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            TurnStreamFinal.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.sessionId);
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.streamId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 3, wireType 0 =*/24).uint64(message.seq);
                if (message.sampleIndex != null && Object.hasOwnProperty.call(message, "sampleIndex"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.sampleIndex);
                return writer;
            };

            /**
             * Encodes the specified TurnStreamFinal message, length delimited. Does not implicitly {@link fluent_audio.v1.TurnStreamFinal.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.TurnStreamFinal
             * @static
             * @param {fluent_audio.v1.ITurnStreamFinal} message TurnStreamFinal message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            TurnStreamFinal.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes a TurnStreamFinal message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.TurnStreamFinal
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.TurnStreamFinal} TurnStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            TurnStreamFinal.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.TurnStreamFinal();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 2: {
                            message.streamId = reader.string();
                            break;
                        }
                    case 3: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 4: {
                            message.sampleIndex = reader.uint64();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes a TurnStreamFinal message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.TurnStreamFinal
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.TurnStreamFinal} TurnStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            TurnStreamFinal.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a TurnStreamFinal message.
             * @function verify
             * @memberof fluent_audio.v1.TurnStreamFinal
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            TurnStreamFinal.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    if (!$util.isString(message.streamId))
                        return "streamId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.sampleIndex != null && Object.hasOwnProperty.call(message, "sampleIndex"))
                    if (!$util.isInteger(message.sampleIndex) && !(message.sampleIndex && $util.isInteger(message.sampleIndex.low) && $util.isInteger(message.sampleIndex.high)))
                        return "sampleIndex: integer|Long expected";
                return null;
            };

            /**
             * Creates a TurnStreamFinal message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.TurnStreamFinal
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.TurnStreamFinal} TurnStreamFinal
             */
            TurnStreamFinal.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.TurnStreamFinal)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.TurnStreamFinal: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.TurnStreamFinal();
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.streamId != null)
                    message.streamId = String(object.streamId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.sampleIndex != null)
                    if ($util.Long)
                        message.sampleIndex = $util.Long.fromValue(object.sampleIndex, true);
                    else if (typeof object.sampleIndex === "string")
                        message.sampleIndex = parseInt(object.sampleIndex, 10);
                    else if (typeof object.sampleIndex === "number")
                        message.sampleIndex = object.sampleIndex;
                    else if (typeof object.sampleIndex === "object")
                        message.sampleIndex = new $util.LongBits(object.sampleIndex.low >>> 0, object.sampleIndex.high >>> 0).toNumber(true);
                return message;
            };

            /**
             * Creates a plain object from a TurnStreamFinal message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.TurnStreamFinal
             * @static
             * @param {fluent_audio.v1.TurnStreamFinal} message TurnStreamFinal
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            TurnStreamFinal.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.sessionId = "";
                    object.streamId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.sampleIndex = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.sampleIndex = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                }
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    object.streamId = message.streamId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.sampleIndex != null && Object.hasOwnProperty.call(message, "sampleIndex"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.sampleIndex = typeof message.sampleIndex === "number" ? BigInt(message.sampleIndex) : $util.Long.fromBits(message.sampleIndex.low >>> 0, message.sampleIndex.high >>> 0, true).toBigInt();
                    else if (typeof message.sampleIndex === "number")
                        object.sampleIndex = options.longs === String ? String(message.sampleIndex) : message.sampleIndex;
                    else
                        object.sampleIndex = options.longs === String ? $util.Long.prototype.toString.call(message.sampleIndex) : options.longs === Number ? new $util.LongBits(message.sampleIndex.low >>> 0, message.sampleIndex.high >>> 0).toNumber(true) : message.sampleIndex;
                return object;
            };

            /**
             * Converts this TurnStreamFinal to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.TurnStreamFinal
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            TurnStreamFinal.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for TurnStreamFinal
             * @function getTypeUrl
             * @memberof fluent_audio.v1.TurnStreamFinal
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            TurnStreamFinal.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.TurnStreamFinal";
            };

            return TurnStreamFinal;
        })();

        v1.AsrStart = (function() {

            /**
             * Properties of an AsrStart.
             * @memberof fluent_audio.v1
             * @interface IAsrStart
             * @property {string|null} [sessionId] AsrStart sessionId
             * @property {string|null} [userTurnId] AsrStart userTurnId
             * @property {string|null} [streamId] AsrStart streamId
             * @property {number|Long|null} [seq] AsrStart seq
             * @property {number|Long|null} [startSampleIndex] AsrStart startSampleIndex
             */

            /**
             * Constructs a new AsrStart.
             * @memberof fluent_audio.v1
             * @classdesc Represents an AsrStart.
             * @implements IAsrStart
             * @constructor
             * @param {fluent_audio.v1.IAsrStart=} [properties] Properties to set
             */
            function AsrStart(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * AsrStart sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.AsrStart
             * @instance
             */
            AsrStart.prototype.sessionId = "";

            /**
             * AsrStart userTurnId.
             * @member {string} userTurnId
             * @memberof fluent_audio.v1.AsrStart
             * @instance
             */
            AsrStart.prototype.userTurnId = "";

            /**
             * AsrStart streamId.
             * @member {string} streamId
             * @memberof fluent_audio.v1.AsrStart
             * @instance
             */
            AsrStart.prototype.streamId = "";

            /**
             * AsrStart seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.AsrStart
             * @instance
             */
            AsrStart.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * AsrStart startSampleIndex.
             * @member {number|Long} startSampleIndex
             * @memberof fluent_audio.v1.AsrStart
             * @instance
             */
            AsrStart.prototype.startSampleIndex = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * Creates a new AsrStart instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.AsrStart
             * @static
             * @param {fluent_audio.v1.IAsrStart=} [properties] Properties to set
             * @returns {fluent_audio.v1.AsrStart} AsrStart instance
             */
            AsrStart.create = function create(properties) {
                return new AsrStart(properties);
            };

            /**
             * Encodes the specified AsrStart message. Does not implicitly {@link fluent_audio.v1.AsrStart.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.AsrStart
             * @static
             * @param {fluent_audio.v1.IAsrStart} message AsrStart message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AsrStart.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.sessionId);
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.userTurnId);
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.streamId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.seq);
                if (message.startSampleIndex != null && Object.hasOwnProperty.call(message, "startSampleIndex"))
                    writer.uint32(/* id 5, wireType 0 =*/40).uint64(message.startSampleIndex);
                return writer;
            };

            /**
             * Encodes the specified AsrStart message, length delimited. Does not implicitly {@link fluent_audio.v1.AsrStart.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.AsrStart
             * @static
             * @param {fluent_audio.v1.IAsrStart} message AsrStart message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AsrStart.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes an AsrStart message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.AsrStart
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.AsrStart} AsrStart
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AsrStart.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.AsrStart();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 2: {
                            message.userTurnId = reader.string();
                            break;
                        }
                    case 3: {
                            message.streamId = reader.string();
                            break;
                        }
                    case 4: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 5: {
                            message.startSampleIndex = reader.uint64();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes an AsrStart message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.AsrStart
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.AsrStart} AsrStart
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AsrStart.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies an AsrStart message.
             * @function verify
             * @memberof fluent_audio.v1.AsrStart
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            AsrStart.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    if (!$util.isString(message.userTurnId))
                        return "userTurnId: string expected";
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    if (!$util.isString(message.streamId))
                        return "streamId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.startSampleIndex != null && Object.hasOwnProperty.call(message, "startSampleIndex"))
                    if (!$util.isInteger(message.startSampleIndex) && !(message.startSampleIndex && $util.isInteger(message.startSampleIndex.low) && $util.isInteger(message.startSampleIndex.high)))
                        return "startSampleIndex: integer|Long expected";
                return null;
            };

            /**
             * Creates an AsrStart message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.AsrStart
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.AsrStart} AsrStart
             */
            AsrStart.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.AsrStart)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.AsrStart: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.AsrStart();
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.userTurnId != null)
                    message.userTurnId = String(object.userTurnId);
                if (object.streamId != null)
                    message.streamId = String(object.streamId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.startSampleIndex != null)
                    if ($util.Long)
                        message.startSampleIndex = $util.Long.fromValue(object.startSampleIndex, true);
                    else if (typeof object.startSampleIndex === "string")
                        message.startSampleIndex = parseInt(object.startSampleIndex, 10);
                    else if (typeof object.startSampleIndex === "number")
                        message.startSampleIndex = object.startSampleIndex;
                    else if (typeof object.startSampleIndex === "object")
                        message.startSampleIndex = new $util.LongBits(object.startSampleIndex.low >>> 0, object.startSampleIndex.high >>> 0).toNumber(true);
                return message;
            };

            /**
             * Creates a plain object from an AsrStart message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.AsrStart
             * @static
             * @param {fluent_audio.v1.AsrStart} message AsrStart
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            AsrStart.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.sessionId = "";
                    object.userTurnId = "";
                    object.streamId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.startSampleIndex = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.startSampleIndex = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                }
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    object.userTurnId = message.userTurnId;
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    object.streamId = message.streamId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.startSampleIndex != null && Object.hasOwnProperty.call(message, "startSampleIndex"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.startSampleIndex = typeof message.startSampleIndex === "number" ? BigInt(message.startSampleIndex) : $util.Long.fromBits(message.startSampleIndex.low >>> 0, message.startSampleIndex.high >>> 0, true).toBigInt();
                    else if (typeof message.startSampleIndex === "number")
                        object.startSampleIndex = options.longs === String ? String(message.startSampleIndex) : message.startSampleIndex;
                    else
                        object.startSampleIndex = options.longs === String ? $util.Long.prototype.toString.call(message.startSampleIndex) : options.longs === Number ? new $util.LongBits(message.startSampleIndex.low >>> 0, message.startSampleIndex.high >>> 0).toNumber(true) : message.startSampleIndex;
                return object;
            };

            /**
             * Converts this AsrStart to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.AsrStart
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            AsrStart.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for AsrStart
             * @function getTypeUrl
             * @memberof fluent_audio.v1.AsrStart
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            AsrStart.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.AsrStart";
            };

            return AsrStart;
        })();

        v1.AsrStop = (function() {

            /**
             * Properties of an AsrStop.
             * @memberof fluent_audio.v1
             * @interface IAsrStop
             * @property {string|null} [sessionId] AsrStop sessionId
             * @property {string|null} [userTurnId] AsrStop userTurnId
             * @property {string|null} [streamId] AsrStop streamId
             * @property {number|Long|null} [seq] AsrStop seq
             * @property {number|Long|null} [stopSampleIndex] AsrStop stopSampleIndex
             */

            /**
             * Constructs a new AsrStop.
             * @memberof fluent_audio.v1
             * @classdesc Represents an AsrStop.
             * @implements IAsrStop
             * @constructor
             * @param {fluent_audio.v1.IAsrStop=} [properties] Properties to set
             */
            function AsrStop(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * AsrStop sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.AsrStop
             * @instance
             */
            AsrStop.prototype.sessionId = "";

            /**
             * AsrStop userTurnId.
             * @member {string} userTurnId
             * @memberof fluent_audio.v1.AsrStop
             * @instance
             */
            AsrStop.prototype.userTurnId = "";

            /**
             * AsrStop streamId.
             * @member {string} streamId
             * @memberof fluent_audio.v1.AsrStop
             * @instance
             */
            AsrStop.prototype.streamId = "";

            /**
             * AsrStop seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.AsrStop
             * @instance
             */
            AsrStop.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * AsrStop stopSampleIndex.
             * @member {number|Long} stopSampleIndex
             * @memberof fluent_audio.v1.AsrStop
             * @instance
             */
            AsrStop.prototype.stopSampleIndex = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * Creates a new AsrStop instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.AsrStop
             * @static
             * @param {fluent_audio.v1.IAsrStop=} [properties] Properties to set
             * @returns {fluent_audio.v1.AsrStop} AsrStop instance
             */
            AsrStop.create = function create(properties) {
                return new AsrStop(properties);
            };

            /**
             * Encodes the specified AsrStop message. Does not implicitly {@link fluent_audio.v1.AsrStop.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.AsrStop
             * @static
             * @param {fluent_audio.v1.IAsrStop} message AsrStop message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AsrStop.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.sessionId);
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.userTurnId);
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.streamId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.seq);
                if (message.stopSampleIndex != null && Object.hasOwnProperty.call(message, "stopSampleIndex"))
                    writer.uint32(/* id 5, wireType 0 =*/40).uint64(message.stopSampleIndex);
                return writer;
            };

            /**
             * Encodes the specified AsrStop message, length delimited. Does not implicitly {@link fluent_audio.v1.AsrStop.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.AsrStop
             * @static
             * @param {fluent_audio.v1.IAsrStop} message AsrStop message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AsrStop.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes an AsrStop message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.AsrStop
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.AsrStop} AsrStop
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AsrStop.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.AsrStop();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 2: {
                            message.userTurnId = reader.string();
                            break;
                        }
                    case 3: {
                            message.streamId = reader.string();
                            break;
                        }
                    case 4: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 5: {
                            message.stopSampleIndex = reader.uint64();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes an AsrStop message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.AsrStop
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.AsrStop} AsrStop
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AsrStop.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies an AsrStop message.
             * @function verify
             * @memberof fluent_audio.v1.AsrStop
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            AsrStop.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    if (!$util.isString(message.userTurnId))
                        return "userTurnId: string expected";
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    if (!$util.isString(message.streamId))
                        return "streamId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.stopSampleIndex != null && Object.hasOwnProperty.call(message, "stopSampleIndex"))
                    if (!$util.isInteger(message.stopSampleIndex) && !(message.stopSampleIndex && $util.isInteger(message.stopSampleIndex.low) && $util.isInteger(message.stopSampleIndex.high)))
                        return "stopSampleIndex: integer|Long expected";
                return null;
            };

            /**
             * Creates an AsrStop message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.AsrStop
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.AsrStop} AsrStop
             */
            AsrStop.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.AsrStop)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.AsrStop: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.AsrStop();
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.userTurnId != null)
                    message.userTurnId = String(object.userTurnId);
                if (object.streamId != null)
                    message.streamId = String(object.streamId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.stopSampleIndex != null)
                    if ($util.Long)
                        message.stopSampleIndex = $util.Long.fromValue(object.stopSampleIndex, true);
                    else if (typeof object.stopSampleIndex === "string")
                        message.stopSampleIndex = parseInt(object.stopSampleIndex, 10);
                    else if (typeof object.stopSampleIndex === "number")
                        message.stopSampleIndex = object.stopSampleIndex;
                    else if (typeof object.stopSampleIndex === "object")
                        message.stopSampleIndex = new $util.LongBits(object.stopSampleIndex.low >>> 0, object.stopSampleIndex.high >>> 0).toNumber(true);
                return message;
            };

            /**
             * Creates a plain object from an AsrStop message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.AsrStop
             * @static
             * @param {fluent_audio.v1.AsrStop} message AsrStop
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            AsrStop.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.sessionId = "";
                    object.userTurnId = "";
                    object.streamId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.stopSampleIndex = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.stopSampleIndex = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                }
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    object.userTurnId = message.userTurnId;
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    object.streamId = message.streamId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.stopSampleIndex != null && Object.hasOwnProperty.call(message, "stopSampleIndex"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.stopSampleIndex = typeof message.stopSampleIndex === "number" ? BigInt(message.stopSampleIndex) : $util.Long.fromBits(message.stopSampleIndex.low >>> 0, message.stopSampleIndex.high >>> 0, true).toBigInt();
                    else if (typeof message.stopSampleIndex === "number")
                        object.stopSampleIndex = options.longs === String ? String(message.stopSampleIndex) : message.stopSampleIndex;
                    else
                        object.stopSampleIndex = options.longs === String ? $util.Long.prototype.toString.call(message.stopSampleIndex) : options.longs === Number ? new $util.LongBits(message.stopSampleIndex.low >>> 0, message.stopSampleIndex.high >>> 0).toNumber(true) : message.stopSampleIndex;
                return object;
            };

            /**
             * Converts this AsrStop to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.AsrStop
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            AsrStop.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for AsrStop
             * @function getTypeUrl
             * @memberof fluent_audio.v1.AsrStop
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            AsrStop.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.AsrStop";
            };

            return AsrStop;
        })();

        v1.AsrCancel = (function() {

            /**
             * Properties of an AsrCancel.
             * @memberof fluent_audio.v1
             * @interface IAsrCancel
             * @property {string|null} [sessionId] AsrCancel sessionId
             * @property {string|null} [userTurnId] AsrCancel userTurnId
             * @property {string|null} [streamId] AsrCancel streamId
             * @property {number|Long|null} [seq] AsrCancel seq
             * @property {string|null} [reason] AsrCancel reason
             */

            /**
             * Constructs a new AsrCancel.
             * @memberof fluent_audio.v1
             * @classdesc Represents an AsrCancel.
             * @implements IAsrCancel
             * @constructor
             * @param {fluent_audio.v1.IAsrCancel=} [properties] Properties to set
             */
            function AsrCancel(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * AsrCancel sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.AsrCancel
             * @instance
             */
            AsrCancel.prototype.sessionId = "";

            /**
             * AsrCancel userTurnId.
             * @member {string} userTurnId
             * @memberof fluent_audio.v1.AsrCancel
             * @instance
             */
            AsrCancel.prototype.userTurnId = "";

            /**
             * AsrCancel streamId.
             * @member {string} streamId
             * @memberof fluent_audio.v1.AsrCancel
             * @instance
             */
            AsrCancel.prototype.streamId = "";

            /**
             * AsrCancel seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.AsrCancel
             * @instance
             */
            AsrCancel.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * AsrCancel reason.
             * @member {string} reason
             * @memberof fluent_audio.v1.AsrCancel
             * @instance
             */
            AsrCancel.prototype.reason = "";

            /**
             * Creates a new AsrCancel instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.AsrCancel
             * @static
             * @param {fluent_audio.v1.IAsrCancel=} [properties] Properties to set
             * @returns {fluent_audio.v1.AsrCancel} AsrCancel instance
             */
            AsrCancel.create = function create(properties) {
                return new AsrCancel(properties);
            };

            /**
             * Encodes the specified AsrCancel message. Does not implicitly {@link fluent_audio.v1.AsrCancel.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.AsrCancel
             * @static
             * @param {fluent_audio.v1.IAsrCancel} message AsrCancel message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AsrCancel.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.sessionId);
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.userTurnId);
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.streamId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.seq);
                if (message.reason != null && Object.hasOwnProperty.call(message, "reason"))
                    writer.uint32(/* id 5, wireType 2 =*/42).string(message.reason);
                return writer;
            };

            /**
             * Encodes the specified AsrCancel message, length delimited. Does not implicitly {@link fluent_audio.v1.AsrCancel.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.AsrCancel
             * @static
             * @param {fluent_audio.v1.IAsrCancel} message AsrCancel message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AsrCancel.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes an AsrCancel message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.AsrCancel
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.AsrCancel} AsrCancel
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AsrCancel.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.AsrCancel();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 2: {
                            message.userTurnId = reader.string();
                            break;
                        }
                    case 3: {
                            message.streamId = reader.string();
                            break;
                        }
                    case 4: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 5: {
                            message.reason = reader.string();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes an AsrCancel message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.AsrCancel
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.AsrCancel} AsrCancel
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AsrCancel.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies an AsrCancel message.
             * @function verify
             * @memberof fluent_audio.v1.AsrCancel
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            AsrCancel.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    if (!$util.isString(message.userTurnId))
                        return "userTurnId: string expected";
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    if (!$util.isString(message.streamId))
                        return "streamId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.reason != null && Object.hasOwnProperty.call(message, "reason"))
                    if (!$util.isString(message.reason))
                        return "reason: string expected";
                return null;
            };

            /**
             * Creates an AsrCancel message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.AsrCancel
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.AsrCancel} AsrCancel
             */
            AsrCancel.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.AsrCancel)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.AsrCancel: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.AsrCancel();
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.userTurnId != null)
                    message.userTurnId = String(object.userTurnId);
                if (object.streamId != null)
                    message.streamId = String(object.streamId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.reason != null)
                    message.reason = String(object.reason);
                return message;
            };

            /**
             * Creates a plain object from an AsrCancel message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.AsrCancel
             * @static
             * @param {fluent_audio.v1.AsrCancel} message AsrCancel
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            AsrCancel.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.sessionId = "";
                    object.userTurnId = "";
                    object.streamId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    object.reason = "";
                }
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    object.userTurnId = message.userTurnId;
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    object.streamId = message.streamId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.reason != null && Object.hasOwnProperty.call(message, "reason"))
                    object.reason = message.reason;
                return object;
            };

            /**
             * Converts this AsrCancel to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.AsrCancel
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            AsrCancel.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for AsrCancel
             * @function getTypeUrl
             * @memberof fluent_audio.v1.AsrCancel
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            AsrCancel.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.AsrCancel";
            };

            return AsrCancel;
        })();

        v1.AsrControl = (function() {

            /**
             * Properties of an AsrControl.
             * @memberof fluent_audio.v1
             * @interface IAsrControl
             * @property {fluent_audio.v1.IAsrStart|null} [start] AsrControl start
             * @property {fluent_audio.v1.IAsrStop|null} [stop] AsrControl stop
             * @property {fluent_audio.v1.IAsrCancel|null} [cancel] AsrControl cancel
             */

            /**
             * Constructs a new AsrControl.
             * @memberof fluent_audio.v1
             * @classdesc Represents an AsrControl.
             * @implements IAsrControl
             * @constructor
             * @param {fluent_audio.v1.IAsrControl=} [properties] Properties to set
             */
            function AsrControl(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * AsrControl start.
             * @member {fluent_audio.v1.IAsrStart|null|undefined} start
             * @memberof fluent_audio.v1.AsrControl
             * @instance
             */
            AsrControl.prototype.start = null;

            /**
             * AsrControl stop.
             * @member {fluent_audio.v1.IAsrStop|null|undefined} stop
             * @memberof fluent_audio.v1.AsrControl
             * @instance
             */
            AsrControl.prototype.stop = null;

            /**
             * AsrControl cancel.
             * @member {fluent_audio.v1.IAsrCancel|null|undefined} cancel
             * @memberof fluent_audio.v1.AsrControl
             * @instance
             */
            AsrControl.prototype.cancel = null;

            // OneOf field names bound to virtual getters and setters
            var $oneOfFields;

            /**
             * AsrControl control.
             * @member {"start"|"stop"|"cancel"|undefined} control
             * @memberof fluent_audio.v1.AsrControl
             * @instance
             */
            Object.defineProperty(AsrControl.prototype, "control", {
                get: $util.oneOfGetter($oneOfFields = ["start", "stop", "cancel"]),
                set: $util.oneOfSetter($oneOfFields)
            });

            /**
             * Creates a new AsrControl instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.AsrControl
             * @static
             * @param {fluent_audio.v1.IAsrControl=} [properties] Properties to set
             * @returns {fluent_audio.v1.AsrControl} AsrControl instance
             */
            AsrControl.create = function create(properties) {
                return new AsrControl(properties);
            };

            /**
             * Encodes the specified AsrControl message. Does not implicitly {@link fluent_audio.v1.AsrControl.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.AsrControl
             * @static
             * @param {fluent_audio.v1.IAsrControl} message AsrControl message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AsrControl.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.start != null && Object.hasOwnProperty.call(message, "start"))
                    $root.fluent_audio.v1.AsrStart.encode(message.start, writer.uint32(/* id 1, wireType 2 =*/10).fork(), q + 1).ldelim();
                if (message.stop != null && Object.hasOwnProperty.call(message, "stop"))
                    $root.fluent_audio.v1.AsrStop.encode(message.stop, writer.uint32(/* id 2, wireType 2 =*/18).fork(), q + 1).ldelim();
                if (message.cancel != null && Object.hasOwnProperty.call(message, "cancel"))
                    $root.fluent_audio.v1.AsrCancel.encode(message.cancel, writer.uint32(/* id 3, wireType 2 =*/26).fork(), q + 1).ldelim();
                return writer;
            };

            /**
             * Encodes the specified AsrControl message, length delimited. Does not implicitly {@link fluent_audio.v1.AsrControl.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.AsrControl
             * @static
             * @param {fluent_audio.v1.IAsrControl} message AsrControl message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AsrControl.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes an AsrControl message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.AsrControl
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.AsrControl} AsrControl
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AsrControl.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.AsrControl();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.start = $root.fluent_audio.v1.AsrStart.decode(reader, reader.uint32(), undefined, long + 1);
                            break;
                        }
                    case 2: {
                            message.stop = $root.fluent_audio.v1.AsrStop.decode(reader, reader.uint32(), undefined, long + 1);
                            break;
                        }
                    case 3: {
                            message.cancel = $root.fluent_audio.v1.AsrCancel.decode(reader, reader.uint32(), undefined, long + 1);
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes an AsrControl message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.AsrControl
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.AsrControl} AsrControl
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AsrControl.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies an AsrControl message.
             * @function verify
             * @memberof fluent_audio.v1.AsrControl
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            AsrControl.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                var properties = {};
                if (message.start != null && Object.hasOwnProperty.call(message, "start")) {
                    properties.control = 1;
                    {
                        var error = $root.fluent_audio.v1.AsrStart.verify(message.start, long + 1);
                        if (error)
                            return "start." + error;
                    }
                }
                if (message.stop != null && Object.hasOwnProperty.call(message, "stop")) {
                    if (properties.control === 1)
                        return "control: multiple values";
                    properties.control = 1;
                    {
                        var error = $root.fluent_audio.v1.AsrStop.verify(message.stop, long + 1);
                        if (error)
                            return "stop." + error;
                    }
                }
                if (message.cancel != null && Object.hasOwnProperty.call(message, "cancel")) {
                    if (properties.control === 1)
                        return "control: multiple values";
                    properties.control = 1;
                    {
                        var error = $root.fluent_audio.v1.AsrCancel.verify(message.cancel, long + 1);
                        if (error)
                            return "cancel." + error;
                    }
                }
                return null;
            };

            /**
             * Creates an AsrControl message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.AsrControl
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.AsrControl} AsrControl
             */
            AsrControl.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.AsrControl)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.AsrControl: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.AsrControl();
                if (object.start != null) {
                    if (!$util.isObject(object.start))
                        throw TypeError(".fluent_audio.v1.AsrControl.start: object expected");
                    message.start = $root.fluent_audio.v1.AsrStart.fromObject(object.start, long + 1);
                }
                if (object.stop != null) {
                    if (!$util.isObject(object.stop))
                        throw TypeError(".fluent_audio.v1.AsrControl.stop: object expected");
                    message.stop = $root.fluent_audio.v1.AsrStop.fromObject(object.stop, long + 1);
                }
                if (object.cancel != null) {
                    if (!$util.isObject(object.cancel))
                        throw TypeError(".fluent_audio.v1.AsrControl.cancel: object expected");
                    message.cancel = $root.fluent_audio.v1.AsrCancel.fromObject(object.cancel, long + 1);
                }
                return message;
            };

            /**
             * Creates a plain object from an AsrControl message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.AsrControl
             * @static
             * @param {fluent_audio.v1.AsrControl} message AsrControl
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            AsrControl.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (message.start != null && Object.hasOwnProperty.call(message, "start")) {
                    object.start = $root.fluent_audio.v1.AsrStart.toObject(message.start, options, q + 1);
                    if (options.oneofs)
                        object.control = "start";
                }
                if (message.stop != null && Object.hasOwnProperty.call(message, "stop")) {
                    object.stop = $root.fluent_audio.v1.AsrStop.toObject(message.stop, options, q + 1);
                    if (options.oneofs)
                        object.control = "stop";
                }
                if (message.cancel != null && Object.hasOwnProperty.call(message, "cancel")) {
                    object.cancel = $root.fluent_audio.v1.AsrCancel.toObject(message.cancel, options, q + 1);
                    if (options.oneofs)
                        object.control = "cancel";
                }
                return object;
            };

            /**
             * Converts this AsrControl to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.AsrControl
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            AsrControl.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for AsrControl
             * @function getTypeUrl
             * @memberof fluent_audio.v1.AsrControl
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            AsrControl.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.AsrControl";
            };

            return AsrControl;
        })();

        v1.AsrControlStreamFinal = (function() {

            /**
             * Properties of an AsrControlStreamFinal.
             * @memberof fluent_audio.v1
             * @interface IAsrControlStreamFinal
             * @property {string|null} [sessionId] AsrControlStreamFinal sessionId
             * @property {string|null} [streamId] AsrControlStreamFinal streamId
             * @property {number|Long|null} [seq] AsrControlStreamFinal seq
             */

            /**
             * Constructs a new AsrControlStreamFinal.
             * @memberof fluent_audio.v1
             * @classdesc Represents an AsrControlStreamFinal.
             * @implements IAsrControlStreamFinal
             * @constructor
             * @param {fluent_audio.v1.IAsrControlStreamFinal=} [properties] Properties to set
             */
            function AsrControlStreamFinal(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * AsrControlStreamFinal sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.AsrControlStreamFinal
             * @instance
             */
            AsrControlStreamFinal.prototype.sessionId = "";

            /**
             * AsrControlStreamFinal streamId.
             * @member {string} streamId
             * @memberof fluent_audio.v1.AsrControlStreamFinal
             * @instance
             */
            AsrControlStreamFinal.prototype.streamId = "";

            /**
             * AsrControlStreamFinal seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.AsrControlStreamFinal
             * @instance
             */
            AsrControlStreamFinal.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * Creates a new AsrControlStreamFinal instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.AsrControlStreamFinal
             * @static
             * @param {fluent_audio.v1.IAsrControlStreamFinal=} [properties] Properties to set
             * @returns {fluent_audio.v1.AsrControlStreamFinal} AsrControlStreamFinal instance
             */
            AsrControlStreamFinal.create = function create(properties) {
                return new AsrControlStreamFinal(properties);
            };

            /**
             * Encodes the specified AsrControlStreamFinal message. Does not implicitly {@link fluent_audio.v1.AsrControlStreamFinal.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.AsrControlStreamFinal
             * @static
             * @param {fluent_audio.v1.IAsrControlStreamFinal} message AsrControlStreamFinal message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AsrControlStreamFinal.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.sessionId);
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.streamId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 3, wireType 0 =*/24).uint64(message.seq);
                return writer;
            };

            /**
             * Encodes the specified AsrControlStreamFinal message, length delimited. Does not implicitly {@link fluent_audio.v1.AsrControlStreamFinal.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.AsrControlStreamFinal
             * @static
             * @param {fluent_audio.v1.IAsrControlStreamFinal} message AsrControlStreamFinal message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AsrControlStreamFinal.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes an AsrControlStreamFinal message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.AsrControlStreamFinal
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.AsrControlStreamFinal} AsrControlStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AsrControlStreamFinal.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.AsrControlStreamFinal();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 2: {
                            message.streamId = reader.string();
                            break;
                        }
                    case 3: {
                            message.seq = reader.uint64();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes an AsrControlStreamFinal message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.AsrControlStreamFinal
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.AsrControlStreamFinal} AsrControlStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AsrControlStreamFinal.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies an AsrControlStreamFinal message.
             * @function verify
             * @memberof fluent_audio.v1.AsrControlStreamFinal
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            AsrControlStreamFinal.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    if (!$util.isString(message.streamId))
                        return "streamId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                return null;
            };

            /**
             * Creates an AsrControlStreamFinal message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.AsrControlStreamFinal
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.AsrControlStreamFinal} AsrControlStreamFinal
             */
            AsrControlStreamFinal.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.AsrControlStreamFinal)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.AsrControlStreamFinal: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.AsrControlStreamFinal();
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.streamId != null)
                    message.streamId = String(object.streamId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                return message;
            };

            /**
             * Creates a plain object from an AsrControlStreamFinal message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.AsrControlStreamFinal
             * @static
             * @param {fluent_audio.v1.AsrControlStreamFinal} message AsrControlStreamFinal
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            AsrControlStreamFinal.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.sessionId = "";
                    object.streamId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                }
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    object.streamId = message.streamId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                return object;
            };

            /**
             * Converts this AsrControlStreamFinal to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.AsrControlStreamFinal
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            AsrControlStreamFinal.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for AsrControlStreamFinal
             * @function getTypeUrl
             * @memberof fluent_audio.v1.AsrControlStreamFinal
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            AsrControlStreamFinal.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.AsrControlStreamFinal";
            };

            return AsrControlStreamFinal;
        })();

        v1.TranscriptDelta = (function() {

            /**
             * Properties of a TranscriptDelta.
             * @memberof fluent_audio.v1
             * @interface ITranscriptDelta
             * @property {string|null} [sessionId] TranscriptDelta sessionId
             * @property {string|null} [userTurnId] TranscriptDelta userTurnId
             * @property {string|null} [streamId] TranscriptDelta streamId
             * @property {number|Long|null} [seq] TranscriptDelta seq
             * @property {string|null} [text] TranscriptDelta text
             */

            /**
             * Constructs a new TranscriptDelta.
             * @memberof fluent_audio.v1
             * @classdesc Represents a TranscriptDelta.
             * @implements ITranscriptDelta
             * @constructor
             * @param {fluent_audio.v1.ITranscriptDelta=} [properties] Properties to set
             */
            function TranscriptDelta(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * TranscriptDelta sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.TranscriptDelta
             * @instance
             */
            TranscriptDelta.prototype.sessionId = "";

            /**
             * TranscriptDelta userTurnId.
             * @member {string} userTurnId
             * @memberof fluent_audio.v1.TranscriptDelta
             * @instance
             */
            TranscriptDelta.prototype.userTurnId = "";

            /**
             * TranscriptDelta streamId.
             * @member {string} streamId
             * @memberof fluent_audio.v1.TranscriptDelta
             * @instance
             */
            TranscriptDelta.prototype.streamId = "";

            /**
             * TranscriptDelta seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.TranscriptDelta
             * @instance
             */
            TranscriptDelta.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * TranscriptDelta text.
             * @member {string} text
             * @memberof fluent_audio.v1.TranscriptDelta
             * @instance
             */
            TranscriptDelta.prototype.text = "";

            /**
             * Creates a new TranscriptDelta instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.TranscriptDelta
             * @static
             * @param {fluent_audio.v1.ITranscriptDelta=} [properties] Properties to set
             * @returns {fluent_audio.v1.TranscriptDelta} TranscriptDelta instance
             */
            TranscriptDelta.create = function create(properties) {
                return new TranscriptDelta(properties);
            };

            /**
             * Encodes the specified TranscriptDelta message. Does not implicitly {@link fluent_audio.v1.TranscriptDelta.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.TranscriptDelta
             * @static
             * @param {fluent_audio.v1.ITranscriptDelta} message TranscriptDelta message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            TranscriptDelta.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.sessionId);
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.userTurnId);
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.streamId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.seq);
                if (message.text != null && Object.hasOwnProperty.call(message, "text"))
                    writer.uint32(/* id 5, wireType 2 =*/42).string(message.text);
                return writer;
            };

            /**
             * Encodes the specified TranscriptDelta message, length delimited. Does not implicitly {@link fluent_audio.v1.TranscriptDelta.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.TranscriptDelta
             * @static
             * @param {fluent_audio.v1.ITranscriptDelta} message TranscriptDelta message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            TranscriptDelta.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes a TranscriptDelta message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.TranscriptDelta
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.TranscriptDelta} TranscriptDelta
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            TranscriptDelta.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.TranscriptDelta();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 2: {
                            message.userTurnId = reader.string();
                            break;
                        }
                    case 3: {
                            message.streamId = reader.string();
                            break;
                        }
                    case 4: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 5: {
                            message.text = reader.string();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes a TranscriptDelta message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.TranscriptDelta
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.TranscriptDelta} TranscriptDelta
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            TranscriptDelta.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a TranscriptDelta message.
             * @function verify
             * @memberof fluent_audio.v1.TranscriptDelta
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            TranscriptDelta.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    if (!$util.isString(message.userTurnId))
                        return "userTurnId: string expected";
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    if (!$util.isString(message.streamId))
                        return "streamId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.text != null && Object.hasOwnProperty.call(message, "text"))
                    if (!$util.isString(message.text))
                        return "text: string expected";
                return null;
            };

            /**
             * Creates a TranscriptDelta message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.TranscriptDelta
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.TranscriptDelta} TranscriptDelta
             */
            TranscriptDelta.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.TranscriptDelta)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.TranscriptDelta: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.TranscriptDelta();
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.userTurnId != null)
                    message.userTurnId = String(object.userTurnId);
                if (object.streamId != null)
                    message.streamId = String(object.streamId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.text != null)
                    message.text = String(object.text);
                return message;
            };

            /**
             * Creates a plain object from a TranscriptDelta message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.TranscriptDelta
             * @static
             * @param {fluent_audio.v1.TranscriptDelta} message TranscriptDelta
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            TranscriptDelta.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.sessionId = "";
                    object.userTurnId = "";
                    object.streamId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    object.text = "";
                }
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    object.userTurnId = message.userTurnId;
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    object.streamId = message.streamId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.text != null && Object.hasOwnProperty.call(message, "text"))
                    object.text = message.text;
                return object;
            };

            /**
             * Converts this TranscriptDelta to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.TranscriptDelta
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            TranscriptDelta.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for TranscriptDelta
             * @function getTypeUrl
             * @memberof fluent_audio.v1.TranscriptDelta
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            TranscriptDelta.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.TranscriptDelta";
            };

            return TranscriptDelta;
        })();

        v1.TranscriptPartial = (function() {

            /**
             * Properties of a TranscriptPartial.
             * @memberof fluent_audio.v1
             * @interface ITranscriptPartial
             * @property {string|null} [sessionId] TranscriptPartial sessionId
             * @property {string|null} [userTurnId] TranscriptPartial userTurnId
             * @property {string|null} [streamId] TranscriptPartial streamId
             * @property {number|Long|null} [seq] TranscriptPartial seq
             * @property {string|null} [text] TranscriptPartial text
             */

            /**
             * Constructs a new TranscriptPartial.
             * @memberof fluent_audio.v1
             * @classdesc Represents a TranscriptPartial.
             * @implements ITranscriptPartial
             * @constructor
             * @param {fluent_audio.v1.ITranscriptPartial=} [properties] Properties to set
             */
            function TranscriptPartial(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * TranscriptPartial sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.TranscriptPartial
             * @instance
             */
            TranscriptPartial.prototype.sessionId = "";

            /**
             * TranscriptPartial userTurnId.
             * @member {string} userTurnId
             * @memberof fluent_audio.v1.TranscriptPartial
             * @instance
             */
            TranscriptPartial.prototype.userTurnId = "";

            /**
             * TranscriptPartial streamId.
             * @member {string} streamId
             * @memberof fluent_audio.v1.TranscriptPartial
             * @instance
             */
            TranscriptPartial.prototype.streamId = "";

            /**
             * TranscriptPartial seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.TranscriptPartial
             * @instance
             */
            TranscriptPartial.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * TranscriptPartial text.
             * @member {string} text
             * @memberof fluent_audio.v1.TranscriptPartial
             * @instance
             */
            TranscriptPartial.prototype.text = "";

            /**
             * Creates a new TranscriptPartial instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.TranscriptPartial
             * @static
             * @param {fluent_audio.v1.ITranscriptPartial=} [properties] Properties to set
             * @returns {fluent_audio.v1.TranscriptPartial} TranscriptPartial instance
             */
            TranscriptPartial.create = function create(properties) {
                return new TranscriptPartial(properties);
            };

            /**
             * Encodes the specified TranscriptPartial message. Does not implicitly {@link fluent_audio.v1.TranscriptPartial.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.TranscriptPartial
             * @static
             * @param {fluent_audio.v1.ITranscriptPartial} message TranscriptPartial message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            TranscriptPartial.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.sessionId);
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.userTurnId);
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.streamId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.seq);
                if (message.text != null && Object.hasOwnProperty.call(message, "text"))
                    writer.uint32(/* id 5, wireType 2 =*/42).string(message.text);
                return writer;
            };

            /**
             * Encodes the specified TranscriptPartial message, length delimited. Does not implicitly {@link fluent_audio.v1.TranscriptPartial.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.TranscriptPartial
             * @static
             * @param {fluent_audio.v1.ITranscriptPartial} message TranscriptPartial message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            TranscriptPartial.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes a TranscriptPartial message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.TranscriptPartial
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.TranscriptPartial} TranscriptPartial
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            TranscriptPartial.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.TranscriptPartial();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 2: {
                            message.userTurnId = reader.string();
                            break;
                        }
                    case 3: {
                            message.streamId = reader.string();
                            break;
                        }
                    case 4: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 5: {
                            message.text = reader.string();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes a TranscriptPartial message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.TranscriptPartial
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.TranscriptPartial} TranscriptPartial
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            TranscriptPartial.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a TranscriptPartial message.
             * @function verify
             * @memberof fluent_audio.v1.TranscriptPartial
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            TranscriptPartial.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    if (!$util.isString(message.userTurnId))
                        return "userTurnId: string expected";
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    if (!$util.isString(message.streamId))
                        return "streamId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.text != null && Object.hasOwnProperty.call(message, "text"))
                    if (!$util.isString(message.text))
                        return "text: string expected";
                return null;
            };

            /**
             * Creates a TranscriptPartial message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.TranscriptPartial
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.TranscriptPartial} TranscriptPartial
             */
            TranscriptPartial.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.TranscriptPartial)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.TranscriptPartial: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.TranscriptPartial();
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.userTurnId != null)
                    message.userTurnId = String(object.userTurnId);
                if (object.streamId != null)
                    message.streamId = String(object.streamId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.text != null)
                    message.text = String(object.text);
                return message;
            };

            /**
             * Creates a plain object from a TranscriptPartial message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.TranscriptPartial
             * @static
             * @param {fluent_audio.v1.TranscriptPartial} message TranscriptPartial
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            TranscriptPartial.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.sessionId = "";
                    object.userTurnId = "";
                    object.streamId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    object.text = "";
                }
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    object.userTurnId = message.userTurnId;
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    object.streamId = message.streamId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.text != null && Object.hasOwnProperty.call(message, "text"))
                    object.text = message.text;
                return object;
            };

            /**
             * Converts this TranscriptPartial to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.TranscriptPartial
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            TranscriptPartial.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for TranscriptPartial
             * @function getTypeUrl
             * @memberof fluent_audio.v1.TranscriptPartial
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            TranscriptPartial.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.TranscriptPartial";
            };

            return TranscriptPartial;
        })();

        v1.TranscriptFinal = (function() {

            /**
             * Properties of a TranscriptFinal.
             * @memberof fluent_audio.v1
             * @interface ITranscriptFinal
             * @property {string|null} [sessionId] TranscriptFinal sessionId
             * @property {string|null} [userTurnId] TranscriptFinal userTurnId
             * @property {string|null} [streamId] TranscriptFinal streamId
             * @property {number|Long|null} [seq] TranscriptFinal seq
             * @property {string|null} [text] TranscriptFinal text
             * @property {number|Long|null} [startSampleIndex] TranscriptFinal startSampleIndex
             * @property {number|Long|null} [endSampleIndex] TranscriptFinal endSampleIndex
             */

            /**
             * Constructs a new TranscriptFinal.
             * @memberof fluent_audio.v1
             * @classdesc Represents a TranscriptFinal.
             * @implements ITranscriptFinal
             * @constructor
             * @param {fluent_audio.v1.ITranscriptFinal=} [properties] Properties to set
             */
            function TranscriptFinal(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * TranscriptFinal sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.TranscriptFinal
             * @instance
             */
            TranscriptFinal.prototype.sessionId = "";

            /**
             * TranscriptFinal userTurnId.
             * @member {string} userTurnId
             * @memberof fluent_audio.v1.TranscriptFinal
             * @instance
             */
            TranscriptFinal.prototype.userTurnId = "";

            /**
             * TranscriptFinal streamId.
             * @member {string} streamId
             * @memberof fluent_audio.v1.TranscriptFinal
             * @instance
             */
            TranscriptFinal.prototype.streamId = "";

            /**
             * TranscriptFinal seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.TranscriptFinal
             * @instance
             */
            TranscriptFinal.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * TranscriptFinal text.
             * @member {string} text
             * @memberof fluent_audio.v1.TranscriptFinal
             * @instance
             */
            TranscriptFinal.prototype.text = "";

            /**
             * TranscriptFinal startSampleIndex.
             * @member {number|Long} startSampleIndex
             * @memberof fluent_audio.v1.TranscriptFinal
             * @instance
             */
            TranscriptFinal.prototype.startSampleIndex = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * TranscriptFinal endSampleIndex.
             * @member {number|Long} endSampleIndex
             * @memberof fluent_audio.v1.TranscriptFinal
             * @instance
             */
            TranscriptFinal.prototype.endSampleIndex = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * Creates a new TranscriptFinal instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.TranscriptFinal
             * @static
             * @param {fluent_audio.v1.ITranscriptFinal=} [properties] Properties to set
             * @returns {fluent_audio.v1.TranscriptFinal} TranscriptFinal instance
             */
            TranscriptFinal.create = function create(properties) {
                return new TranscriptFinal(properties);
            };

            /**
             * Encodes the specified TranscriptFinal message. Does not implicitly {@link fluent_audio.v1.TranscriptFinal.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.TranscriptFinal
             * @static
             * @param {fluent_audio.v1.ITranscriptFinal} message TranscriptFinal message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            TranscriptFinal.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.sessionId);
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.userTurnId);
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.streamId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.seq);
                if (message.text != null && Object.hasOwnProperty.call(message, "text"))
                    writer.uint32(/* id 5, wireType 2 =*/42).string(message.text);
                if (message.startSampleIndex != null && Object.hasOwnProperty.call(message, "startSampleIndex"))
                    writer.uint32(/* id 6, wireType 0 =*/48).uint64(message.startSampleIndex);
                if (message.endSampleIndex != null && Object.hasOwnProperty.call(message, "endSampleIndex"))
                    writer.uint32(/* id 7, wireType 0 =*/56).uint64(message.endSampleIndex);
                return writer;
            };

            /**
             * Encodes the specified TranscriptFinal message, length delimited. Does not implicitly {@link fluent_audio.v1.TranscriptFinal.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.TranscriptFinal
             * @static
             * @param {fluent_audio.v1.ITranscriptFinal} message TranscriptFinal message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            TranscriptFinal.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes a TranscriptFinal message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.TranscriptFinal
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.TranscriptFinal} TranscriptFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            TranscriptFinal.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.TranscriptFinal();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 2: {
                            message.userTurnId = reader.string();
                            break;
                        }
                    case 3: {
                            message.streamId = reader.string();
                            break;
                        }
                    case 4: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 5: {
                            message.text = reader.string();
                            break;
                        }
                    case 6: {
                            message.startSampleIndex = reader.uint64();
                            break;
                        }
                    case 7: {
                            message.endSampleIndex = reader.uint64();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes a TranscriptFinal message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.TranscriptFinal
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.TranscriptFinal} TranscriptFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            TranscriptFinal.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a TranscriptFinal message.
             * @function verify
             * @memberof fluent_audio.v1.TranscriptFinal
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            TranscriptFinal.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    if (!$util.isString(message.userTurnId))
                        return "userTurnId: string expected";
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    if (!$util.isString(message.streamId))
                        return "streamId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.text != null && Object.hasOwnProperty.call(message, "text"))
                    if (!$util.isString(message.text))
                        return "text: string expected";
                if (message.startSampleIndex != null && Object.hasOwnProperty.call(message, "startSampleIndex"))
                    if (!$util.isInteger(message.startSampleIndex) && !(message.startSampleIndex && $util.isInteger(message.startSampleIndex.low) && $util.isInteger(message.startSampleIndex.high)))
                        return "startSampleIndex: integer|Long expected";
                if (message.endSampleIndex != null && Object.hasOwnProperty.call(message, "endSampleIndex"))
                    if (!$util.isInteger(message.endSampleIndex) && !(message.endSampleIndex && $util.isInteger(message.endSampleIndex.low) && $util.isInteger(message.endSampleIndex.high)))
                        return "endSampleIndex: integer|Long expected";
                return null;
            };

            /**
             * Creates a TranscriptFinal message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.TranscriptFinal
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.TranscriptFinal} TranscriptFinal
             */
            TranscriptFinal.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.TranscriptFinal)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.TranscriptFinal: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.TranscriptFinal();
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.userTurnId != null)
                    message.userTurnId = String(object.userTurnId);
                if (object.streamId != null)
                    message.streamId = String(object.streamId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.text != null)
                    message.text = String(object.text);
                if (object.startSampleIndex != null)
                    if ($util.Long)
                        message.startSampleIndex = $util.Long.fromValue(object.startSampleIndex, true);
                    else if (typeof object.startSampleIndex === "string")
                        message.startSampleIndex = parseInt(object.startSampleIndex, 10);
                    else if (typeof object.startSampleIndex === "number")
                        message.startSampleIndex = object.startSampleIndex;
                    else if (typeof object.startSampleIndex === "object")
                        message.startSampleIndex = new $util.LongBits(object.startSampleIndex.low >>> 0, object.startSampleIndex.high >>> 0).toNumber(true);
                if (object.endSampleIndex != null)
                    if ($util.Long)
                        message.endSampleIndex = $util.Long.fromValue(object.endSampleIndex, true);
                    else if (typeof object.endSampleIndex === "string")
                        message.endSampleIndex = parseInt(object.endSampleIndex, 10);
                    else if (typeof object.endSampleIndex === "number")
                        message.endSampleIndex = object.endSampleIndex;
                    else if (typeof object.endSampleIndex === "object")
                        message.endSampleIndex = new $util.LongBits(object.endSampleIndex.low >>> 0, object.endSampleIndex.high >>> 0).toNumber(true);
                return message;
            };

            /**
             * Creates a plain object from a TranscriptFinal message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.TranscriptFinal
             * @static
             * @param {fluent_audio.v1.TranscriptFinal} message TranscriptFinal
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            TranscriptFinal.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.sessionId = "";
                    object.userTurnId = "";
                    object.streamId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    object.text = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.startSampleIndex = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.startSampleIndex = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.endSampleIndex = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.endSampleIndex = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                }
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    object.userTurnId = message.userTurnId;
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    object.streamId = message.streamId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.text != null && Object.hasOwnProperty.call(message, "text"))
                    object.text = message.text;
                if (message.startSampleIndex != null && Object.hasOwnProperty.call(message, "startSampleIndex"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.startSampleIndex = typeof message.startSampleIndex === "number" ? BigInt(message.startSampleIndex) : $util.Long.fromBits(message.startSampleIndex.low >>> 0, message.startSampleIndex.high >>> 0, true).toBigInt();
                    else if (typeof message.startSampleIndex === "number")
                        object.startSampleIndex = options.longs === String ? String(message.startSampleIndex) : message.startSampleIndex;
                    else
                        object.startSampleIndex = options.longs === String ? $util.Long.prototype.toString.call(message.startSampleIndex) : options.longs === Number ? new $util.LongBits(message.startSampleIndex.low >>> 0, message.startSampleIndex.high >>> 0).toNumber(true) : message.startSampleIndex;
                if (message.endSampleIndex != null && Object.hasOwnProperty.call(message, "endSampleIndex"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.endSampleIndex = typeof message.endSampleIndex === "number" ? BigInt(message.endSampleIndex) : $util.Long.fromBits(message.endSampleIndex.low >>> 0, message.endSampleIndex.high >>> 0, true).toBigInt();
                    else if (typeof message.endSampleIndex === "number")
                        object.endSampleIndex = options.longs === String ? String(message.endSampleIndex) : message.endSampleIndex;
                    else
                        object.endSampleIndex = options.longs === String ? $util.Long.prototype.toString.call(message.endSampleIndex) : options.longs === Number ? new $util.LongBits(message.endSampleIndex.low >>> 0, message.endSampleIndex.high >>> 0).toNumber(true) : message.endSampleIndex;
                return object;
            };

            /**
             * Converts this TranscriptFinal to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.TranscriptFinal
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            TranscriptFinal.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for TranscriptFinal
             * @function getTypeUrl
             * @memberof fluent_audio.v1.TranscriptFinal
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            TranscriptFinal.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.TranscriptFinal";
            };

            return TranscriptFinal;
        })();

        v1.TranscriptEvent = (function() {

            /**
             * Properties of a TranscriptEvent.
             * @memberof fluent_audio.v1
             * @interface ITranscriptEvent
             * @property {fluent_audio.v1.ITranscriptDelta|null} [delta] TranscriptEvent delta
             * @property {fluent_audio.v1.ITranscriptFinal|null} [final] TranscriptEvent final
             * @property {fluent_audio.v1.ITranscriptPartial|null} [partial] TranscriptEvent partial
             */

            /**
             * Constructs a new TranscriptEvent.
             * @memberof fluent_audio.v1
             * @classdesc Represents a TranscriptEvent.
             * @implements ITranscriptEvent
             * @constructor
             * @param {fluent_audio.v1.ITranscriptEvent=} [properties] Properties to set
             */
            function TranscriptEvent(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * TranscriptEvent delta.
             * @member {fluent_audio.v1.ITranscriptDelta|null|undefined} delta
             * @memberof fluent_audio.v1.TranscriptEvent
             * @instance
             */
            TranscriptEvent.prototype.delta = null;

            /**
             * TranscriptEvent final.
             * @member {fluent_audio.v1.ITranscriptFinal|null|undefined} final
             * @memberof fluent_audio.v1.TranscriptEvent
             * @instance
             */
            TranscriptEvent.prototype.final = null;

            /**
             * TranscriptEvent partial.
             * @member {fluent_audio.v1.ITranscriptPartial|null|undefined} partial
             * @memberof fluent_audio.v1.TranscriptEvent
             * @instance
             */
            TranscriptEvent.prototype.partial = null;

            // OneOf field names bound to virtual getters and setters
            var $oneOfFields;

            /**
             * TranscriptEvent event.
             * @member {"delta"|"final"|"partial"|undefined} event
             * @memberof fluent_audio.v1.TranscriptEvent
             * @instance
             */
            Object.defineProperty(TranscriptEvent.prototype, "event", {
                get: $util.oneOfGetter($oneOfFields = ["delta", "final", "partial"]),
                set: $util.oneOfSetter($oneOfFields)
            });

            /**
             * Creates a new TranscriptEvent instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.TranscriptEvent
             * @static
             * @param {fluent_audio.v1.ITranscriptEvent=} [properties] Properties to set
             * @returns {fluent_audio.v1.TranscriptEvent} TranscriptEvent instance
             */
            TranscriptEvent.create = function create(properties) {
                return new TranscriptEvent(properties);
            };

            /**
             * Encodes the specified TranscriptEvent message. Does not implicitly {@link fluent_audio.v1.TranscriptEvent.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.TranscriptEvent
             * @static
             * @param {fluent_audio.v1.ITranscriptEvent} message TranscriptEvent message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            TranscriptEvent.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.delta != null && Object.hasOwnProperty.call(message, "delta"))
                    $root.fluent_audio.v1.TranscriptDelta.encode(message.delta, writer.uint32(/* id 1, wireType 2 =*/10).fork(), q + 1).ldelim();
                if (message.final != null && Object.hasOwnProperty.call(message, "final"))
                    $root.fluent_audio.v1.TranscriptFinal.encode(message.final, writer.uint32(/* id 2, wireType 2 =*/18).fork(), q + 1).ldelim();
                if (message.partial != null && Object.hasOwnProperty.call(message, "partial"))
                    $root.fluent_audio.v1.TranscriptPartial.encode(message.partial, writer.uint32(/* id 3, wireType 2 =*/26).fork(), q + 1).ldelim();
                return writer;
            };

            /**
             * Encodes the specified TranscriptEvent message, length delimited. Does not implicitly {@link fluent_audio.v1.TranscriptEvent.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.TranscriptEvent
             * @static
             * @param {fluent_audio.v1.ITranscriptEvent} message TranscriptEvent message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            TranscriptEvent.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes a TranscriptEvent message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.TranscriptEvent
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.TranscriptEvent} TranscriptEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            TranscriptEvent.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.TranscriptEvent();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.delta = $root.fluent_audio.v1.TranscriptDelta.decode(reader, reader.uint32(), undefined, long + 1);
                            break;
                        }
                    case 2: {
                            message.final = $root.fluent_audio.v1.TranscriptFinal.decode(reader, reader.uint32(), undefined, long + 1);
                            break;
                        }
                    case 3: {
                            message.partial = $root.fluent_audio.v1.TranscriptPartial.decode(reader, reader.uint32(), undefined, long + 1);
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes a TranscriptEvent message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.TranscriptEvent
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.TranscriptEvent} TranscriptEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            TranscriptEvent.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a TranscriptEvent message.
             * @function verify
             * @memberof fluent_audio.v1.TranscriptEvent
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            TranscriptEvent.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                var properties = {};
                if (message.delta != null && Object.hasOwnProperty.call(message, "delta")) {
                    properties.event = 1;
                    {
                        var error = $root.fluent_audio.v1.TranscriptDelta.verify(message.delta, long + 1);
                        if (error)
                            return "delta." + error;
                    }
                }
                if (message.final != null && Object.hasOwnProperty.call(message, "final")) {
                    if (properties.event === 1)
                        return "event: multiple values";
                    properties.event = 1;
                    {
                        var error = $root.fluent_audio.v1.TranscriptFinal.verify(message.final, long + 1);
                        if (error)
                            return "final." + error;
                    }
                }
                if (message.partial != null && Object.hasOwnProperty.call(message, "partial")) {
                    if (properties.event === 1)
                        return "event: multiple values";
                    properties.event = 1;
                    {
                        var error = $root.fluent_audio.v1.TranscriptPartial.verify(message.partial, long + 1);
                        if (error)
                            return "partial." + error;
                    }
                }
                return null;
            };

            /**
             * Creates a TranscriptEvent message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.TranscriptEvent
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.TranscriptEvent} TranscriptEvent
             */
            TranscriptEvent.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.TranscriptEvent)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.TranscriptEvent: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.TranscriptEvent();
                if (object.delta != null) {
                    if (!$util.isObject(object.delta))
                        throw TypeError(".fluent_audio.v1.TranscriptEvent.delta: object expected");
                    message.delta = $root.fluent_audio.v1.TranscriptDelta.fromObject(object.delta, long + 1);
                }
                if (object.final != null) {
                    if (!$util.isObject(object.final))
                        throw TypeError(".fluent_audio.v1.TranscriptEvent.final: object expected");
                    message.final = $root.fluent_audio.v1.TranscriptFinal.fromObject(object.final, long + 1);
                }
                if (object.partial != null) {
                    if (!$util.isObject(object.partial))
                        throw TypeError(".fluent_audio.v1.TranscriptEvent.partial: object expected");
                    message.partial = $root.fluent_audio.v1.TranscriptPartial.fromObject(object.partial, long + 1);
                }
                return message;
            };

            /**
             * Creates a plain object from a TranscriptEvent message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.TranscriptEvent
             * @static
             * @param {fluent_audio.v1.TranscriptEvent} message TranscriptEvent
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            TranscriptEvent.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (message.delta != null && Object.hasOwnProperty.call(message, "delta")) {
                    object.delta = $root.fluent_audio.v1.TranscriptDelta.toObject(message.delta, options, q + 1);
                    if (options.oneofs)
                        object.event = "delta";
                }
                if (message.final != null && Object.hasOwnProperty.call(message, "final")) {
                    object.final = $root.fluent_audio.v1.TranscriptFinal.toObject(message.final, options, q + 1);
                    if (options.oneofs)
                        object.event = "final";
                }
                if (message.partial != null && Object.hasOwnProperty.call(message, "partial")) {
                    object.partial = $root.fluent_audio.v1.TranscriptPartial.toObject(message.partial, options, q + 1);
                    if (options.oneofs)
                        object.event = "partial";
                }
                return object;
            };

            /**
             * Converts this TranscriptEvent to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.TranscriptEvent
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            TranscriptEvent.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for TranscriptEvent
             * @function getTypeUrl
             * @memberof fluent_audio.v1.TranscriptEvent
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            TranscriptEvent.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.TranscriptEvent";
            };

            return TranscriptEvent;
        })();

        v1.TranscriptStreamFinal = (function() {

            /**
             * Properties of a TranscriptStreamFinal.
             * @memberof fluent_audio.v1
             * @interface ITranscriptStreamFinal
             * @property {string|null} [sessionId] TranscriptStreamFinal sessionId
             * @property {string|null} [streamId] TranscriptStreamFinal streamId
             * @property {number|Long|null} [seq] TranscriptStreamFinal seq
             * @property {number|Long|null} [sampleIndex] TranscriptStreamFinal sampleIndex
             */

            /**
             * Constructs a new TranscriptStreamFinal.
             * @memberof fluent_audio.v1
             * @classdesc Represents a TranscriptStreamFinal.
             * @implements ITranscriptStreamFinal
             * @constructor
             * @param {fluent_audio.v1.ITranscriptStreamFinal=} [properties] Properties to set
             */
            function TranscriptStreamFinal(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * TranscriptStreamFinal sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.TranscriptStreamFinal
             * @instance
             */
            TranscriptStreamFinal.prototype.sessionId = "";

            /**
             * TranscriptStreamFinal streamId.
             * @member {string} streamId
             * @memberof fluent_audio.v1.TranscriptStreamFinal
             * @instance
             */
            TranscriptStreamFinal.prototype.streamId = "";

            /**
             * TranscriptStreamFinal seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.TranscriptStreamFinal
             * @instance
             */
            TranscriptStreamFinal.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * TranscriptStreamFinal sampleIndex.
             * @member {number|Long} sampleIndex
             * @memberof fluent_audio.v1.TranscriptStreamFinal
             * @instance
             */
            TranscriptStreamFinal.prototype.sampleIndex = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * Creates a new TranscriptStreamFinal instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.TranscriptStreamFinal
             * @static
             * @param {fluent_audio.v1.ITranscriptStreamFinal=} [properties] Properties to set
             * @returns {fluent_audio.v1.TranscriptStreamFinal} TranscriptStreamFinal instance
             */
            TranscriptStreamFinal.create = function create(properties) {
                return new TranscriptStreamFinal(properties);
            };

            /**
             * Encodes the specified TranscriptStreamFinal message. Does not implicitly {@link fluent_audio.v1.TranscriptStreamFinal.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.TranscriptStreamFinal
             * @static
             * @param {fluent_audio.v1.ITranscriptStreamFinal} message TranscriptStreamFinal message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            TranscriptStreamFinal.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.sessionId);
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.streamId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 3, wireType 0 =*/24).uint64(message.seq);
                if (message.sampleIndex != null && Object.hasOwnProperty.call(message, "sampleIndex"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.sampleIndex);
                return writer;
            };

            /**
             * Encodes the specified TranscriptStreamFinal message, length delimited. Does not implicitly {@link fluent_audio.v1.TranscriptStreamFinal.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.TranscriptStreamFinal
             * @static
             * @param {fluent_audio.v1.ITranscriptStreamFinal} message TranscriptStreamFinal message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            TranscriptStreamFinal.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes a TranscriptStreamFinal message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.TranscriptStreamFinal
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.TranscriptStreamFinal} TranscriptStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            TranscriptStreamFinal.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.TranscriptStreamFinal();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 2: {
                            message.streamId = reader.string();
                            break;
                        }
                    case 3: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 4: {
                            message.sampleIndex = reader.uint64();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes a TranscriptStreamFinal message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.TranscriptStreamFinal
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.TranscriptStreamFinal} TranscriptStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            TranscriptStreamFinal.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a TranscriptStreamFinal message.
             * @function verify
             * @memberof fluent_audio.v1.TranscriptStreamFinal
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            TranscriptStreamFinal.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    if (!$util.isString(message.streamId))
                        return "streamId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.sampleIndex != null && Object.hasOwnProperty.call(message, "sampleIndex"))
                    if (!$util.isInteger(message.sampleIndex) && !(message.sampleIndex && $util.isInteger(message.sampleIndex.low) && $util.isInteger(message.sampleIndex.high)))
                        return "sampleIndex: integer|Long expected";
                return null;
            };

            /**
             * Creates a TranscriptStreamFinal message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.TranscriptStreamFinal
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.TranscriptStreamFinal} TranscriptStreamFinal
             */
            TranscriptStreamFinal.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.TranscriptStreamFinal)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.TranscriptStreamFinal: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.TranscriptStreamFinal();
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.streamId != null)
                    message.streamId = String(object.streamId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.sampleIndex != null)
                    if ($util.Long)
                        message.sampleIndex = $util.Long.fromValue(object.sampleIndex, true);
                    else if (typeof object.sampleIndex === "string")
                        message.sampleIndex = parseInt(object.sampleIndex, 10);
                    else if (typeof object.sampleIndex === "number")
                        message.sampleIndex = object.sampleIndex;
                    else if (typeof object.sampleIndex === "object")
                        message.sampleIndex = new $util.LongBits(object.sampleIndex.low >>> 0, object.sampleIndex.high >>> 0).toNumber(true);
                return message;
            };

            /**
             * Creates a plain object from a TranscriptStreamFinal message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.TranscriptStreamFinal
             * @static
             * @param {fluent_audio.v1.TranscriptStreamFinal} message TranscriptStreamFinal
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            TranscriptStreamFinal.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.sessionId = "";
                    object.streamId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.sampleIndex = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.sampleIndex = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                }
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    object.streamId = message.streamId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.sampleIndex != null && Object.hasOwnProperty.call(message, "sampleIndex"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.sampleIndex = typeof message.sampleIndex === "number" ? BigInt(message.sampleIndex) : $util.Long.fromBits(message.sampleIndex.low >>> 0, message.sampleIndex.high >>> 0, true).toBigInt();
                    else if (typeof message.sampleIndex === "number")
                        object.sampleIndex = options.longs === String ? String(message.sampleIndex) : message.sampleIndex;
                    else
                        object.sampleIndex = options.longs === String ? $util.Long.prototype.toString.call(message.sampleIndex) : options.longs === Number ? new $util.LongBits(message.sampleIndex.low >>> 0, message.sampleIndex.high >>> 0).toNumber(true) : message.sampleIndex;
                return object;
            };

            /**
             * Converts this TranscriptStreamFinal to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.TranscriptStreamFinal
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            TranscriptStreamFinal.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for TranscriptStreamFinal
             * @function getTypeUrl
             * @memberof fluent_audio.v1.TranscriptStreamFinal
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            TranscriptStreamFinal.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.TranscriptStreamFinal";
            };

            return TranscriptStreamFinal;
        })();

        /**
         * DialogueInputKind enum.
         * @name fluent_audio.v1.DialogueInputKind
         * @enum {number}
         * @property {number} DIALOGUE_INPUT_KIND_UNSPECIFIED=0 DIALOGUE_INPUT_KIND_UNSPECIFIED value
         * @property {number} DIALOGUE_INPUT_KIND_TRANSCRIPT_FINAL=1 DIALOGUE_INPUT_KIND_TRANSCRIPT_FINAL value
         * @property {number} DIALOGUE_INPUT_KIND_CANCEL=2 DIALOGUE_INPUT_KIND_CANCEL value
         * @property {number} DIALOGUE_INPUT_KIND_PLAYBACK_DONE=3 DIALOGUE_INPUT_KIND_PLAYBACK_DONE value
         */
        v1.DialogueInputKind = (function() {
            var valuesById = {}, values = Object.create(valuesById);
            values[valuesById[0] = "DIALOGUE_INPUT_KIND_UNSPECIFIED"] = 0;
            values[valuesById[1] = "DIALOGUE_INPUT_KIND_TRANSCRIPT_FINAL"] = 1;
            values[valuesById[2] = "DIALOGUE_INPUT_KIND_CANCEL"] = 2;
            values[valuesById[3] = "DIALOGUE_INPUT_KIND_PLAYBACK_DONE"] = 3;
            return values;
        })();

        /**
         * DialogueEventKind enum.
         * @name fluent_audio.v1.DialogueEventKind
         * @enum {number}
         * @property {number} DIALOGUE_EVENT_KIND_UNSPECIFIED=0 DIALOGUE_EVENT_KIND_UNSPECIFIED value
         * @property {number} DIALOGUE_EVENT_KIND_AGENT_TEXT=1 DIALOGUE_EVENT_KIND_AGENT_TEXT value
         * @property {number} DIALOGUE_EVENT_KIND_TTS_TEXT=2 DIALOGUE_EVENT_KIND_TTS_TEXT value
         * @property {number} DIALOGUE_EVENT_KIND_APPROVAL_REQUESTED=3 DIALOGUE_EVENT_KIND_APPROVAL_REQUESTED value
         * @property {number} DIALOGUE_EVENT_KIND_USER_INPUT_REQUESTED=4 DIALOGUE_EVENT_KIND_USER_INPUT_REQUESTED value
         * @property {number} DIALOGUE_EVENT_KIND_MCP_ELICITATION_REQUESTED=5 DIALOGUE_EVENT_KIND_MCP_ELICITATION_REQUESTED value
         * @property {number} DIALOGUE_EVENT_KIND_TOOL_EVENT=6 DIALOGUE_EVENT_KIND_TOOL_EVENT value
         * @property {number} DIALOGUE_EVENT_KIND_CANCELLED=7 DIALOGUE_EVENT_KIND_CANCELLED value
         * @property {number} DIALOGUE_EVENT_KIND_ERROR=8 DIALOGUE_EVENT_KIND_ERROR value
         */
        v1.DialogueEventKind = (function() {
            var valuesById = {}, values = Object.create(valuesById);
            values[valuesById[0] = "DIALOGUE_EVENT_KIND_UNSPECIFIED"] = 0;
            values[valuesById[1] = "DIALOGUE_EVENT_KIND_AGENT_TEXT"] = 1;
            values[valuesById[2] = "DIALOGUE_EVENT_KIND_TTS_TEXT"] = 2;
            values[valuesById[3] = "DIALOGUE_EVENT_KIND_APPROVAL_REQUESTED"] = 3;
            values[valuesById[4] = "DIALOGUE_EVENT_KIND_USER_INPUT_REQUESTED"] = 4;
            values[valuesById[5] = "DIALOGUE_EVENT_KIND_MCP_ELICITATION_REQUESTED"] = 5;
            values[valuesById[6] = "DIALOGUE_EVENT_KIND_TOOL_EVENT"] = 6;
            values[valuesById[7] = "DIALOGUE_EVENT_KIND_CANCELLED"] = 7;
            values[valuesById[8] = "DIALOGUE_EVENT_KIND_ERROR"] = 8;
            return values;
        })();

        /**
         * AgentApprovalDecision enum.
         * @name fluent_audio.v1.AgentApprovalDecision
         * @enum {number}
         * @property {number} AGENT_APPROVAL_DECISION_UNSPECIFIED=0 AGENT_APPROVAL_DECISION_UNSPECIFIED value
         * @property {number} AGENT_APPROVAL_DECISION_ACCEPT=1 AGENT_APPROVAL_DECISION_ACCEPT value
         * @property {number} AGENT_APPROVAL_DECISION_DECLINE=2 AGENT_APPROVAL_DECISION_DECLINE value
         * @property {number} AGENT_APPROVAL_DECISION_CANCEL=3 AGENT_APPROVAL_DECISION_CANCEL value
         */
        v1.AgentApprovalDecision = (function() {
            var valuesById = {}, values = Object.create(valuesById);
            values[valuesById[0] = "AGENT_APPROVAL_DECISION_UNSPECIFIED"] = 0;
            values[valuesById[1] = "AGENT_APPROVAL_DECISION_ACCEPT"] = 1;
            values[valuesById[2] = "AGENT_APPROVAL_DECISION_DECLINE"] = 2;
            values[valuesById[3] = "AGENT_APPROVAL_DECISION_CANCEL"] = 3;
            return values;
        })();

        /**
         * AgentApprovalScope enum.
         * @name fluent_audio.v1.AgentApprovalScope
         * @enum {number}
         * @property {number} AGENT_APPROVAL_SCOPE_UNSPECIFIED=0 AGENT_APPROVAL_SCOPE_UNSPECIFIED value
         * @property {number} AGENT_APPROVAL_SCOPE_TURN=1 AGENT_APPROVAL_SCOPE_TURN value
         * @property {number} AGENT_APPROVAL_SCOPE_SESSION=2 AGENT_APPROVAL_SCOPE_SESSION value
         */
        v1.AgentApprovalScope = (function() {
            var valuesById = {}, values = Object.create(valuesById);
            values[valuesById[0] = "AGENT_APPROVAL_SCOPE_UNSPECIFIED"] = 0;
            values[valuesById[1] = "AGENT_APPROVAL_SCOPE_TURN"] = 1;
            values[valuesById[2] = "AGENT_APPROVAL_SCOPE_SESSION"] = 2;
            return values;
        })();

        /**
         * AgentToolEventKind enum.
         * @name fluent_audio.v1.AgentToolEventKind
         * @enum {number}
         * @property {number} AGENT_TOOL_EVENT_KIND_UNSPECIFIED=0 AGENT_TOOL_EVENT_KIND_UNSPECIFIED value
         * @property {number} AGENT_TOOL_EVENT_KIND_STARTED=1 AGENT_TOOL_EVENT_KIND_STARTED value
         * @property {number} AGENT_TOOL_EVENT_KIND_COMPLETED=2 AGENT_TOOL_EVENT_KIND_COMPLETED value
         * @property {number} AGENT_TOOL_EVENT_KIND_FAILED=3 AGENT_TOOL_EVENT_KIND_FAILED value
         */
        v1.AgentToolEventKind = (function() {
            var valuesById = {}, values = Object.create(valuesById);
            values[valuesById[0] = "AGENT_TOOL_EVENT_KIND_UNSPECIFIED"] = 0;
            values[valuesById[1] = "AGENT_TOOL_EVENT_KIND_STARTED"] = 1;
            values[valuesById[2] = "AGENT_TOOL_EVENT_KIND_COMPLETED"] = 2;
            values[valuesById[3] = "AGENT_TOOL_EVENT_KIND_FAILED"] = 3;
            return values;
        })();

        /**
         * AgentTurnDoneStatus enum.
         * @name fluent_audio.v1.AgentTurnDoneStatus
         * @enum {number}
         * @property {number} AGENT_TURN_DONE_STATUS_UNSPECIFIED=0 AGENT_TURN_DONE_STATUS_UNSPECIFIED value
         * @property {number} AGENT_TURN_DONE_STATUS_COMPLETED=1 AGENT_TURN_DONE_STATUS_COMPLETED value
         * @property {number} AGENT_TURN_DONE_STATUS_CANCELLED=2 AGENT_TURN_DONE_STATUS_CANCELLED value
         * @property {number} AGENT_TURN_DONE_STATUS_FAILED=3 AGENT_TURN_DONE_STATUS_FAILED value
         */
        v1.AgentTurnDoneStatus = (function() {
            var valuesById = {}, values = Object.create(valuesById);
            values[valuesById[0] = "AGENT_TURN_DONE_STATUS_UNSPECIFIED"] = 0;
            values[valuesById[1] = "AGENT_TURN_DONE_STATUS_COMPLETED"] = 1;
            values[valuesById[2] = "AGENT_TURN_DONE_STATUS_CANCELLED"] = 2;
            values[valuesById[3] = "AGENT_TURN_DONE_STATUS_FAILED"] = 3;
            return values;
        })();

        v1.DialogueInput = (function() {

            /**
             * Properties of a DialogueInput.
             * @memberof fluent_audio.v1
             * @interface IDialogueInput
             * @property {fluent_audio.v1.DialogueInputKind|null} [inputType] DialogueInput inputType
             * @property {string|null} [sessionId] DialogueInput sessionId
             * @property {string|null} [userTurnId] DialogueInput userTurnId
             * @property {number|Long|null} [seq] DialogueInput seq
             * @property {string|null} [text] DialogueInput text
             * @property {string|null} [requestId] DialogueInput requestId
             */

            /**
             * Constructs a new DialogueInput.
             * @memberof fluent_audio.v1
             * @classdesc Represents a DialogueInput.
             * @implements IDialogueInput
             * @constructor
             * @param {fluent_audio.v1.IDialogueInput=} [properties] Properties to set
             */
            function DialogueInput(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * DialogueInput inputType.
             * @member {fluent_audio.v1.DialogueInputKind} inputType
             * @memberof fluent_audio.v1.DialogueInput
             * @instance
             */
            DialogueInput.prototype.inputType = 0;

            /**
             * DialogueInput sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.DialogueInput
             * @instance
             */
            DialogueInput.prototype.sessionId = "";

            /**
             * DialogueInput userTurnId.
             * @member {string} userTurnId
             * @memberof fluent_audio.v1.DialogueInput
             * @instance
             */
            DialogueInput.prototype.userTurnId = "";

            /**
             * DialogueInput seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.DialogueInput
             * @instance
             */
            DialogueInput.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * DialogueInput text.
             * @member {string|null|undefined} text
             * @memberof fluent_audio.v1.DialogueInput
             * @instance
             */
            DialogueInput.prototype.text = null;

            /**
             * DialogueInput requestId.
             * @member {string|null|undefined} requestId
             * @memberof fluent_audio.v1.DialogueInput
             * @instance
             */
            DialogueInput.prototype.requestId = null;

            // OneOf field names bound to virtual getters and setters
            var $oneOfFields;

            // Virtual OneOf for proto3 optional field
            Object.defineProperty(DialogueInput.prototype, "_text", {
                get: $util.oneOfGetter($oneOfFields = ["text"]),
                set: $util.oneOfSetter($oneOfFields)
            });

            // Virtual OneOf for proto3 optional field
            Object.defineProperty(DialogueInput.prototype, "_requestId", {
                get: $util.oneOfGetter($oneOfFields = ["requestId"]),
                set: $util.oneOfSetter($oneOfFields)
            });

            /**
             * Creates a new DialogueInput instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.DialogueInput
             * @static
             * @param {fluent_audio.v1.IDialogueInput=} [properties] Properties to set
             * @returns {fluent_audio.v1.DialogueInput} DialogueInput instance
             */
            DialogueInput.create = function create(properties) {
                return new DialogueInput(properties);
            };

            /**
             * Encodes the specified DialogueInput message. Does not implicitly {@link fluent_audio.v1.DialogueInput.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.DialogueInput
             * @static
             * @param {fluent_audio.v1.IDialogueInput} message DialogueInput message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            DialogueInput.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.inputType != null && Object.hasOwnProperty.call(message, "inputType"))
                    writer.uint32(/* id 1, wireType 0 =*/8).int32(message.inputType);
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.sessionId);
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.userTurnId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.seq);
                if (message.text != null && Object.hasOwnProperty.call(message, "text"))
                    writer.uint32(/* id 5, wireType 2 =*/42).string(message.text);
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    writer.uint32(/* id 6, wireType 2 =*/50).string(message.requestId);
                return writer;
            };

            /**
             * Encodes the specified DialogueInput message, length delimited. Does not implicitly {@link fluent_audio.v1.DialogueInput.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.DialogueInput
             * @static
             * @param {fluent_audio.v1.IDialogueInput} message DialogueInput message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            DialogueInput.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes a DialogueInput message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.DialogueInput
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.DialogueInput} DialogueInput
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            DialogueInput.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.DialogueInput();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.inputType = reader.int32();
                            break;
                        }
                    case 2: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 3: {
                            message.userTurnId = reader.string();
                            break;
                        }
                    case 4: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 5: {
                            message.text = reader.string();
                            break;
                        }
                    case 6: {
                            message.requestId = reader.string();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes a DialogueInput message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.DialogueInput
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.DialogueInput} DialogueInput
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            DialogueInput.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a DialogueInput message.
             * @function verify
             * @memberof fluent_audio.v1.DialogueInput
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            DialogueInput.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                var properties = {};
                if (message.inputType != null && Object.hasOwnProperty.call(message, "inputType"))
                    switch (message.inputType) {
                    default:
                        return "inputType: enum value expected";
                    case 0:
                    case 1:
                    case 2:
                    case 3:
                        break;
                    }
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    if (!$util.isString(message.userTurnId))
                        return "userTurnId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.text != null && Object.hasOwnProperty.call(message, "text")) {
                    properties._text = 1;
                    if (!$util.isString(message.text))
                        return "text: string expected";
                }
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId")) {
                    properties._requestId = 1;
                    if (!$util.isString(message.requestId))
                        return "requestId: string expected";
                }
                return null;
            };

            /**
             * Creates a DialogueInput message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.DialogueInput
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.DialogueInput} DialogueInput
             */
            DialogueInput.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.DialogueInput)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.DialogueInput: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.DialogueInput();
                switch (object.inputType) {
                default:
                    if (typeof object.inputType === "number") {
                        message.inputType = object.inputType;
                        break;
                    }
                    break;
                case "DIALOGUE_INPUT_KIND_UNSPECIFIED":
                case 0:
                    message.inputType = 0;
                    break;
                case "DIALOGUE_INPUT_KIND_TRANSCRIPT_FINAL":
                case 1:
                    message.inputType = 1;
                    break;
                case "DIALOGUE_INPUT_KIND_CANCEL":
                case 2:
                    message.inputType = 2;
                    break;
                case "DIALOGUE_INPUT_KIND_PLAYBACK_DONE":
                case 3:
                    message.inputType = 3;
                    break;
                }
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.userTurnId != null)
                    message.userTurnId = String(object.userTurnId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.text != null)
                    message.text = String(object.text);
                if (object.requestId != null)
                    message.requestId = String(object.requestId);
                return message;
            };

            /**
             * Creates a plain object from a DialogueInput message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.DialogueInput
             * @static
             * @param {fluent_audio.v1.DialogueInput} message DialogueInput
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            DialogueInput.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.inputType = options.enums === String ? "DIALOGUE_INPUT_KIND_UNSPECIFIED" : 0;
                    object.sessionId = "";
                    object.userTurnId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                }
                if (message.inputType != null && Object.hasOwnProperty.call(message, "inputType"))
                    object.inputType = options.enums === String ? $root.fluent_audio.v1.DialogueInputKind[message.inputType] === undefined ? message.inputType : $root.fluent_audio.v1.DialogueInputKind[message.inputType] : message.inputType;
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    object.userTurnId = message.userTurnId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.text != null && Object.hasOwnProperty.call(message, "text")) {
                    object.text = message.text;
                    if (options.oneofs)
                        object._text = "text";
                }
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId")) {
                    object.requestId = message.requestId;
                    if (options.oneofs)
                        object._requestId = "requestId";
                }
                return object;
            };

            /**
             * Converts this DialogueInput to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.DialogueInput
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            DialogueInput.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for DialogueInput
             * @function getTypeUrl
             * @memberof fluent_audio.v1.DialogueInput
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            DialogueInput.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.DialogueInput";
            };

            return DialogueInput;
        })();

        v1.DialogueEvent = (function() {

            /**
             * Properties of a DialogueEvent.
             * @memberof fluent_audio.v1
             * @interface IDialogueEvent
             * @property {fluent_audio.v1.DialogueEventKind|null} [event] DialogueEvent event
             * @property {string|null} [sessionId] DialogueEvent sessionId
             * @property {string|null} [userTurnId] DialogueEvent userTurnId
             * @property {number|Long|null} [seq] DialogueEvent seq
             * @property {string|null} [text] DialogueEvent text
             * @property {string|null} [requestId] DialogueEvent requestId
             * @property {string|null} [message] DialogueEvent message
             */

            /**
             * Constructs a new DialogueEvent.
             * @memberof fluent_audio.v1
             * @classdesc Represents a DialogueEvent.
             * @implements IDialogueEvent
             * @constructor
             * @param {fluent_audio.v1.IDialogueEvent=} [properties] Properties to set
             */
            function DialogueEvent(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * DialogueEvent event.
             * @member {fluent_audio.v1.DialogueEventKind} event
             * @memberof fluent_audio.v1.DialogueEvent
             * @instance
             */
            DialogueEvent.prototype.event = 0;

            /**
             * DialogueEvent sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.DialogueEvent
             * @instance
             */
            DialogueEvent.prototype.sessionId = "";

            /**
             * DialogueEvent userTurnId.
             * @member {string} userTurnId
             * @memberof fluent_audio.v1.DialogueEvent
             * @instance
             */
            DialogueEvent.prototype.userTurnId = "";

            /**
             * DialogueEvent seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.DialogueEvent
             * @instance
             */
            DialogueEvent.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * DialogueEvent text.
             * @member {string|null|undefined} text
             * @memberof fluent_audio.v1.DialogueEvent
             * @instance
             */
            DialogueEvent.prototype.text = null;

            /**
             * DialogueEvent requestId.
             * @member {string|null|undefined} requestId
             * @memberof fluent_audio.v1.DialogueEvent
             * @instance
             */
            DialogueEvent.prototype.requestId = null;

            /**
             * DialogueEvent message.
             * @member {string|null|undefined} message
             * @memberof fluent_audio.v1.DialogueEvent
             * @instance
             */
            DialogueEvent.prototype.message = null;

            // OneOf field names bound to virtual getters and setters
            var $oneOfFields;

            // Virtual OneOf for proto3 optional field
            Object.defineProperty(DialogueEvent.prototype, "_text", {
                get: $util.oneOfGetter($oneOfFields = ["text"]),
                set: $util.oneOfSetter($oneOfFields)
            });

            // Virtual OneOf for proto3 optional field
            Object.defineProperty(DialogueEvent.prototype, "_requestId", {
                get: $util.oneOfGetter($oneOfFields = ["requestId"]),
                set: $util.oneOfSetter($oneOfFields)
            });

            // Virtual OneOf for proto3 optional field
            Object.defineProperty(DialogueEvent.prototype, "_message", {
                get: $util.oneOfGetter($oneOfFields = ["message"]),
                set: $util.oneOfSetter($oneOfFields)
            });

            /**
             * Creates a new DialogueEvent instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.DialogueEvent
             * @static
             * @param {fluent_audio.v1.IDialogueEvent=} [properties] Properties to set
             * @returns {fluent_audio.v1.DialogueEvent} DialogueEvent instance
             */
            DialogueEvent.create = function create(properties) {
                return new DialogueEvent(properties);
            };

            /**
             * Encodes the specified DialogueEvent message. Does not implicitly {@link fluent_audio.v1.DialogueEvent.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.DialogueEvent
             * @static
             * @param {fluent_audio.v1.IDialogueEvent} message DialogueEvent message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            DialogueEvent.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.event != null && Object.hasOwnProperty.call(message, "event"))
                    writer.uint32(/* id 1, wireType 0 =*/8).int32(message.event);
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.sessionId);
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.userTurnId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.seq);
                if (message.text != null && Object.hasOwnProperty.call(message, "text"))
                    writer.uint32(/* id 5, wireType 2 =*/42).string(message.text);
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    writer.uint32(/* id 6, wireType 2 =*/50).string(message.requestId);
                if (message.message != null && Object.hasOwnProperty.call(message, "message"))
                    writer.uint32(/* id 7, wireType 2 =*/58).string(message.message);
                return writer;
            };

            /**
             * Encodes the specified DialogueEvent message, length delimited. Does not implicitly {@link fluent_audio.v1.DialogueEvent.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.DialogueEvent
             * @static
             * @param {fluent_audio.v1.IDialogueEvent} message DialogueEvent message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            DialogueEvent.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes a DialogueEvent message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.DialogueEvent
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.DialogueEvent} DialogueEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            DialogueEvent.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.DialogueEvent();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.event = reader.int32();
                            break;
                        }
                    case 2: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 3: {
                            message.userTurnId = reader.string();
                            break;
                        }
                    case 4: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 5: {
                            message.text = reader.string();
                            break;
                        }
                    case 6: {
                            message.requestId = reader.string();
                            break;
                        }
                    case 7: {
                            message.message = reader.string();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes a DialogueEvent message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.DialogueEvent
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.DialogueEvent} DialogueEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            DialogueEvent.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a DialogueEvent message.
             * @function verify
             * @memberof fluent_audio.v1.DialogueEvent
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            DialogueEvent.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                var properties = {};
                if (message.event != null && Object.hasOwnProperty.call(message, "event"))
                    switch (message.event) {
                    default:
                        return "event: enum value expected";
                    case 0:
                    case 1:
                    case 2:
                    case 3:
                    case 4:
                    case 5:
                    case 6:
                    case 7:
                    case 8:
                        break;
                    }
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    if (!$util.isString(message.userTurnId))
                        return "userTurnId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.text != null && Object.hasOwnProperty.call(message, "text")) {
                    properties._text = 1;
                    if (!$util.isString(message.text))
                        return "text: string expected";
                }
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId")) {
                    properties._requestId = 1;
                    if (!$util.isString(message.requestId))
                        return "requestId: string expected";
                }
                if (message.message != null && Object.hasOwnProperty.call(message, "message")) {
                    properties._message = 1;
                    if (!$util.isString(message.message))
                        return "message: string expected";
                }
                return null;
            };

            /**
             * Creates a DialogueEvent message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.DialogueEvent
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.DialogueEvent} DialogueEvent
             */
            DialogueEvent.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.DialogueEvent)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.DialogueEvent: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.DialogueEvent();
                switch (object.event) {
                default:
                    if (typeof object.event === "number") {
                        message.event = object.event;
                        break;
                    }
                    break;
                case "DIALOGUE_EVENT_KIND_UNSPECIFIED":
                case 0:
                    message.event = 0;
                    break;
                case "DIALOGUE_EVENT_KIND_AGENT_TEXT":
                case 1:
                    message.event = 1;
                    break;
                case "DIALOGUE_EVENT_KIND_TTS_TEXT":
                case 2:
                    message.event = 2;
                    break;
                case "DIALOGUE_EVENT_KIND_APPROVAL_REQUESTED":
                case 3:
                    message.event = 3;
                    break;
                case "DIALOGUE_EVENT_KIND_USER_INPUT_REQUESTED":
                case 4:
                    message.event = 4;
                    break;
                case "DIALOGUE_EVENT_KIND_MCP_ELICITATION_REQUESTED":
                case 5:
                    message.event = 5;
                    break;
                case "DIALOGUE_EVENT_KIND_TOOL_EVENT":
                case 6:
                    message.event = 6;
                    break;
                case "DIALOGUE_EVENT_KIND_CANCELLED":
                case 7:
                    message.event = 7;
                    break;
                case "DIALOGUE_EVENT_KIND_ERROR":
                case 8:
                    message.event = 8;
                    break;
                }
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.userTurnId != null)
                    message.userTurnId = String(object.userTurnId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.text != null)
                    message.text = String(object.text);
                if (object.requestId != null)
                    message.requestId = String(object.requestId);
                if (object.message != null)
                    message.message = String(object.message);
                return message;
            };

            /**
             * Creates a plain object from a DialogueEvent message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.DialogueEvent
             * @static
             * @param {fluent_audio.v1.DialogueEvent} message DialogueEvent
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            DialogueEvent.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.event = options.enums === String ? "DIALOGUE_EVENT_KIND_UNSPECIFIED" : 0;
                    object.sessionId = "";
                    object.userTurnId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                }
                if (message.event != null && Object.hasOwnProperty.call(message, "event"))
                    object.event = options.enums === String ? $root.fluent_audio.v1.DialogueEventKind[message.event] === undefined ? message.event : $root.fluent_audio.v1.DialogueEventKind[message.event] : message.event;
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    object.userTurnId = message.userTurnId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.text != null && Object.hasOwnProperty.call(message, "text")) {
                    object.text = message.text;
                    if (options.oneofs)
                        object._text = "text";
                }
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId")) {
                    object.requestId = message.requestId;
                    if (options.oneofs)
                        object._requestId = "requestId";
                }
                if (message.message != null && Object.hasOwnProperty.call(message, "message")) {
                    object.message = message.message;
                    if (options.oneofs)
                        object._message = "message";
                }
                return object;
            };

            /**
             * Converts this DialogueEvent to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.DialogueEvent
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            DialogueEvent.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for DialogueEvent
             * @function getTypeUrl
             * @memberof fluent_audio.v1.DialogueEvent
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            DialogueEvent.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.DialogueEvent";
            };

            return DialogueEvent;
        })();

        v1.AgentTurnRequest = (function() {

            /**
             * Properties of an AgentTurnRequest.
             * @memberof fluent_audio.v1
             * @interface IAgentTurnRequest
             * @property {string|null} [sessionId] AgentTurnRequest sessionId
             * @property {string|null} [userTurnId] AgentTurnRequest userTurnId
             * @property {string|null} [assistantTurnId] AgentTurnRequest assistantTurnId
             * @property {number|Long|null} [seq] AgentTurnRequest seq
             * @property {string|null} [text] AgentTurnRequest text
             */

            /**
             * Constructs a new AgentTurnRequest.
             * @memberof fluent_audio.v1
             * @classdesc Represents an AgentTurnRequest.
             * @implements IAgentTurnRequest
             * @constructor
             * @param {fluent_audio.v1.IAgentTurnRequest=} [properties] Properties to set
             */
            function AgentTurnRequest(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * AgentTurnRequest sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.AgentTurnRequest
             * @instance
             */
            AgentTurnRequest.prototype.sessionId = "";

            /**
             * AgentTurnRequest userTurnId.
             * @member {string} userTurnId
             * @memberof fluent_audio.v1.AgentTurnRequest
             * @instance
             */
            AgentTurnRequest.prototype.userTurnId = "";

            /**
             * AgentTurnRequest assistantTurnId.
             * @member {string} assistantTurnId
             * @memberof fluent_audio.v1.AgentTurnRequest
             * @instance
             */
            AgentTurnRequest.prototype.assistantTurnId = "";

            /**
             * AgentTurnRequest seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.AgentTurnRequest
             * @instance
             */
            AgentTurnRequest.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * AgentTurnRequest text.
             * @member {string} text
             * @memberof fluent_audio.v1.AgentTurnRequest
             * @instance
             */
            AgentTurnRequest.prototype.text = "";

            /**
             * Creates a new AgentTurnRequest instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.AgentTurnRequest
             * @static
             * @param {fluent_audio.v1.IAgentTurnRequest=} [properties] Properties to set
             * @returns {fluent_audio.v1.AgentTurnRequest} AgentTurnRequest instance
             */
            AgentTurnRequest.create = function create(properties) {
                return new AgentTurnRequest(properties);
            };

            /**
             * Encodes the specified AgentTurnRequest message. Does not implicitly {@link fluent_audio.v1.AgentTurnRequest.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.AgentTurnRequest
             * @static
             * @param {fluent_audio.v1.IAgentTurnRequest} message AgentTurnRequest message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AgentTurnRequest.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.sessionId);
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.userTurnId);
                if (message.assistantTurnId != null && Object.hasOwnProperty.call(message, "assistantTurnId"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.assistantTurnId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.seq);
                if (message.text != null && Object.hasOwnProperty.call(message, "text"))
                    writer.uint32(/* id 5, wireType 2 =*/42).string(message.text);
                return writer;
            };

            /**
             * Encodes the specified AgentTurnRequest message, length delimited. Does not implicitly {@link fluent_audio.v1.AgentTurnRequest.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.AgentTurnRequest
             * @static
             * @param {fluent_audio.v1.IAgentTurnRequest} message AgentTurnRequest message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AgentTurnRequest.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes an AgentTurnRequest message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.AgentTurnRequest
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.AgentTurnRequest} AgentTurnRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AgentTurnRequest.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.AgentTurnRequest();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 2: {
                            message.userTurnId = reader.string();
                            break;
                        }
                    case 3: {
                            message.assistantTurnId = reader.string();
                            break;
                        }
                    case 4: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 5: {
                            message.text = reader.string();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes an AgentTurnRequest message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.AgentTurnRequest
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.AgentTurnRequest} AgentTurnRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AgentTurnRequest.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies an AgentTurnRequest message.
             * @function verify
             * @memberof fluent_audio.v1.AgentTurnRequest
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            AgentTurnRequest.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    if (!$util.isString(message.userTurnId))
                        return "userTurnId: string expected";
                if (message.assistantTurnId != null && Object.hasOwnProperty.call(message, "assistantTurnId"))
                    if (!$util.isString(message.assistantTurnId))
                        return "assistantTurnId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.text != null && Object.hasOwnProperty.call(message, "text"))
                    if (!$util.isString(message.text))
                        return "text: string expected";
                return null;
            };

            /**
             * Creates an AgentTurnRequest message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.AgentTurnRequest
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.AgentTurnRequest} AgentTurnRequest
             */
            AgentTurnRequest.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.AgentTurnRequest)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.AgentTurnRequest: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.AgentTurnRequest();
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.userTurnId != null)
                    message.userTurnId = String(object.userTurnId);
                if (object.assistantTurnId != null)
                    message.assistantTurnId = String(object.assistantTurnId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.text != null)
                    message.text = String(object.text);
                return message;
            };

            /**
             * Creates a plain object from an AgentTurnRequest message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.AgentTurnRequest
             * @static
             * @param {fluent_audio.v1.AgentTurnRequest} message AgentTurnRequest
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            AgentTurnRequest.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.sessionId = "";
                    object.userTurnId = "";
                    object.assistantTurnId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    object.text = "";
                }
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    object.userTurnId = message.userTurnId;
                if (message.assistantTurnId != null && Object.hasOwnProperty.call(message, "assistantTurnId"))
                    object.assistantTurnId = message.assistantTurnId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.text != null && Object.hasOwnProperty.call(message, "text"))
                    object.text = message.text;
                return object;
            };

            /**
             * Converts this AgentTurnRequest to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.AgentTurnRequest
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            AgentTurnRequest.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for AgentTurnRequest
             * @function getTypeUrl
             * @memberof fluent_audio.v1.AgentTurnRequest
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            AgentTurnRequest.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.AgentTurnRequest";
            };

            return AgentTurnRequest;
        })();

        v1.AgentTextDelta = (function() {

            /**
             * Properties of an AgentTextDelta.
             * @memberof fluent_audio.v1
             * @interface IAgentTextDelta
             * @property {string|null} [sessionId] AgentTextDelta sessionId
             * @property {string|null} [userTurnId] AgentTextDelta userTurnId
             * @property {string|null} [agentTurnId] AgentTextDelta agentTurnId
             * @property {number|Long|null} [seq] AgentTextDelta seq
             * @property {string|null} [text] AgentTextDelta text
             */

            /**
             * Constructs a new AgentTextDelta.
             * @memberof fluent_audio.v1
             * @classdesc Represents an AgentTextDelta.
             * @implements IAgentTextDelta
             * @constructor
             * @param {fluent_audio.v1.IAgentTextDelta=} [properties] Properties to set
             */
            function AgentTextDelta(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * AgentTextDelta sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.AgentTextDelta
             * @instance
             */
            AgentTextDelta.prototype.sessionId = "";

            /**
             * AgentTextDelta userTurnId.
             * @member {string} userTurnId
             * @memberof fluent_audio.v1.AgentTextDelta
             * @instance
             */
            AgentTextDelta.prototype.userTurnId = "";

            /**
             * AgentTextDelta agentTurnId.
             * @member {string} agentTurnId
             * @memberof fluent_audio.v1.AgentTextDelta
             * @instance
             */
            AgentTextDelta.prototype.agentTurnId = "";

            /**
             * AgentTextDelta seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.AgentTextDelta
             * @instance
             */
            AgentTextDelta.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * AgentTextDelta text.
             * @member {string} text
             * @memberof fluent_audio.v1.AgentTextDelta
             * @instance
             */
            AgentTextDelta.prototype.text = "";

            /**
             * Creates a new AgentTextDelta instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.AgentTextDelta
             * @static
             * @param {fluent_audio.v1.IAgentTextDelta=} [properties] Properties to set
             * @returns {fluent_audio.v1.AgentTextDelta} AgentTextDelta instance
             */
            AgentTextDelta.create = function create(properties) {
                return new AgentTextDelta(properties);
            };

            /**
             * Encodes the specified AgentTextDelta message. Does not implicitly {@link fluent_audio.v1.AgentTextDelta.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.AgentTextDelta
             * @static
             * @param {fluent_audio.v1.IAgentTextDelta} message AgentTextDelta message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AgentTextDelta.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.sessionId);
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.userTurnId);
                if (message.agentTurnId != null && Object.hasOwnProperty.call(message, "agentTurnId"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.agentTurnId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.seq);
                if (message.text != null && Object.hasOwnProperty.call(message, "text"))
                    writer.uint32(/* id 5, wireType 2 =*/42).string(message.text);
                return writer;
            };

            /**
             * Encodes the specified AgentTextDelta message, length delimited. Does not implicitly {@link fluent_audio.v1.AgentTextDelta.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.AgentTextDelta
             * @static
             * @param {fluent_audio.v1.IAgentTextDelta} message AgentTextDelta message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AgentTextDelta.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes an AgentTextDelta message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.AgentTextDelta
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.AgentTextDelta} AgentTextDelta
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AgentTextDelta.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.AgentTextDelta();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 2: {
                            message.userTurnId = reader.string();
                            break;
                        }
                    case 3: {
                            message.agentTurnId = reader.string();
                            break;
                        }
                    case 4: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 5: {
                            message.text = reader.string();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes an AgentTextDelta message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.AgentTextDelta
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.AgentTextDelta} AgentTextDelta
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AgentTextDelta.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies an AgentTextDelta message.
             * @function verify
             * @memberof fluent_audio.v1.AgentTextDelta
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            AgentTextDelta.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    if (!$util.isString(message.userTurnId))
                        return "userTurnId: string expected";
                if (message.agentTurnId != null && Object.hasOwnProperty.call(message, "agentTurnId"))
                    if (!$util.isString(message.agentTurnId))
                        return "agentTurnId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.text != null && Object.hasOwnProperty.call(message, "text"))
                    if (!$util.isString(message.text))
                        return "text: string expected";
                return null;
            };

            /**
             * Creates an AgentTextDelta message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.AgentTextDelta
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.AgentTextDelta} AgentTextDelta
             */
            AgentTextDelta.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.AgentTextDelta)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.AgentTextDelta: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.AgentTextDelta();
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.userTurnId != null)
                    message.userTurnId = String(object.userTurnId);
                if (object.agentTurnId != null)
                    message.agentTurnId = String(object.agentTurnId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.text != null)
                    message.text = String(object.text);
                return message;
            };

            /**
             * Creates a plain object from an AgentTextDelta message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.AgentTextDelta
             * @static
             * @param {fluent_audio.v1.AgentTextDelta} message AgentTextDelta
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            AgentTextDelta.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.sessionId = "";
                    object.userTurnId = "";
                    object.agentTurnId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    object.text = "";
                }
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    object.userTurnId = message.userTurnId;
                if (message.agentTurnId != null && Object.hasOwnProperty.call(message, "agentTurnId"))
                    object.agentTurnId = message.agentTurnId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.text != null && Object.hasOwnProperty.call(message, "text"))
                    object.text = message.text;
                return object;
            };

            /**
             * Converts this AgentTextDelta to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.AgentTextDelta
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            AgentTextDelta.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for AgentTextDelta
             * @function getTypeUrl
             * @memberof fluent_audio.v1.AgentTextDelta
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            AgentTextDelta.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.AgentTextDelta";
            };

            return AgentTextDelta;
        })();

        v1.AgentTurnDone = (function() {

            /**
             * Properties of an AgentTurnDone.
             * @memberof fluent_audio.v1
             * @interface IAgentTurnDone
             * @property {string|null} [sessionId] AgentTurnDone sessionId
             * @property {string|null} [userTurnId] AgentTurnDone userTurnId
             * @property {string|null} [agentTurnId] AgentTurnDone agentTurnId
             * @property {number|Long|null} [seq] AgentTurnDone seq
             * @property {fluent_audio.v1.AgentTurnDoneStatus|null} [status] AgentTurnDone status
             * @property {string|null} [reason] AgentTurnDone reason
             */

            /**
             * Constructs a new AgentTurnDone.
             * @memberof fluent_audio.v1
             * @classdesc Represents an AgentTurnDone.
             * @implements IAgentTurnDone
             * @constructor
             * @param {fluent_audio.v1.IAgentTurnDone=} [properties] Properties to set
             */
            function AgentTurnDone(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * AgentTurnDone sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.AgentTurnDone
             * @instance
             */
            AgentTurnDone.prototype.sessionId = "";

            /**
             * AgentTurnDone userTurnId.
             * @member {string} userTurnId
             * @memberof fluent_audio.v1.AgentTurnDone
             * @instance
             */
            AgentTurnDone.prototype.userTurnId = "";

            /**
             * AgentTurnDone agentTurnId.
             * @member {string} agentTurnId
             * @memberof fluent_audio.v1.AgentTurnDone
             * @instance
             */
            AgentTurnDone.prototype.agentTurnId = "";

            /**
             * AgentTurnDone seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.AgentTurnDone
             * @instance
             */
            AgentTurnDone.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * AgentTurnDone status.
             * @member {fluent_audio.v1.AgentTurnDoneStatus} status
             * @memberof fluent_audio.v1.AgentTurnDone
             * @instance
             */
            AgentTurnDone.prototype.status = 0;

            /**
             * AgentTurnDone reason.
             * @member {string|null|undefined} reason
             * @memberof fluent_audio.v1.AgentTurnDone
             * @instance
             */
            AgentTurnDone.prototype.reason = null;

            // OneOf field names bound to virtual getters and setters
            var $oneOfFields;

            // Virtual OneOf for proto3 optional field
            Object.defineProperty(AgentTurnDone.prototype, "_reason", {
                get: $util.oneOfGetter($oneOfFields = ["reason"]),
                set: $util.oneOfSetter($oneOfFields)
            });

            /**
             * Creates a new AgentTurnDone instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.AgentTurnDone
             * @static
             * @param {fluent_audio.v1.IAgentTurnDone=} [properties] Properties to set
             * @returns {fluent_audio.v1.AgentTurnDone} AgentTurnDone instance
             */
            AgentTurnDone.create = function create(properties) {
                return new AgentTurnDone(properties);
            };

            /**
             * Encodes the specified AgentTurnDone message. Does not implicitly {@link fluent_audio.v1.AgentTurnDone.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.AgentTurnDone
             * @static
             * @param {fluent_audio.v1.IAgentTurnDone} message AgentTurnDone message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AgentTurnDone.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.sessionId);
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.userTurnId);
                if (message.agentTurnId != null && Object.hasOwnProperty.call(message, "agentTurnId"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.agentTurnId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.seq);
                if (message.status != null && Object.hasOwnProperty.call(message, "status"))
                    writer.uint32(/* id 5, wireType 0 =*/40).int32(message.status);
                if (message.reason != null && Object.hasOwnProperty.call(message, "reason"))
                    writer.uint32(/* id 6, wireType 2 =*/50).string(message.reason);
                return writer;
            };

            /**
             * Encodes the specified AgentTurnDone message, length delimited. Does not implicitly {@link fluent_audio.v1.AgentTurnDone.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.AgentTurnDone
             * @static
             * @param {fluent_audio.v1.IAgentTurnDone} message AgentTurnDone message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AgentTurnDone.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes an AgentTurnDone message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.AgentTurnDone
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.AgentTurnDone} AgentTurnDone
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AgentTurnDone.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.AgentTurnDone();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 2: {
                            message.userTurnId = reader.string();
                            break;
                        }
                    case 3: {
                            message.agentTurnId = reader.string();
                            break;
                        }
                    case 4: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 5: {
                            message.status = reader.int32();
                            break;
                        }
                    case 6: {
                            message.reason = reader.string();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes an AgentTurnDone message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.AgentTurnDone
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.AgentTurnDone} AgentTurnDone
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AgentTurnDone.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies an AgentTurnDone message.
             * @function verify
             * @memberof fluent_audio.v1.AgentTurnDone
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            AgentTurnDone.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                var properties = {};
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    if (!$util.isString(message.userTurnId))
                        return "userTurnId: string expected";
                if (message.agentTurnId != null && Object.hasOwnProperty.call(message, "agentTurnId"))
                    if (!$util.isString(message.agentTurnId))
                        return "agentTurnId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.status != null && Object.hasOwnProperty.call(message, "status"))
                    switch (message.status) {
                    default:
                        return "status: enum value expected";
                    case 0:
                    case 1:
                    case 2:
                    case 3:
                        break;
                    }
                if (message.reason != null && Object.hasOwnProperty.call(message, "reason")) {
                    properties._reason = 1;
                    if (!$util.isString(message.reason))
                        return "reason: string expected";
                }
                return null;
            };

            /**
             * Creates an AgentTurnDone message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.AgentTurnDone
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.AgentTurnDone} AgentTurnDone
             */
            AgentTurnDone.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.AgentTurnDone)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.AgentTurnDone: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.AgentTurnDone();
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.userTurnId != null)
                    message.userTurnId = String(object.userTurnId);
                if (object.agentTurnId != null)
                    message.agentTurnId = String(object.agentTurnId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                switch (object.status) {
                default:
                    if (typeof object.status === "number") {
                        message.status = object.status;
                        break;
                    }
                    break;
                case "AGENT_TURN_DONE_STATUS_UNSPECIFIED":
                case 0:
                    message.status = 0;
                    break;
                case "AGENT_TURN_DONE_STATUS_COMPLETED":
                case 1:
                    message.status = 1;
                    break;
                case "AGENT_TURN_DONE_STATUS_CANCELLED":
                case 2:
                    message.status = 2;
                    break;
                case "AGENT_TURN_DONE_STATUS_FAILED":
                case 3:
                    message.status = 3;
                    break;
                }
                if (object.reason != null)
                    message.reason = String(object.reason);
                return message;
            };

            /**
             * Creates a plain object from an AgentTurnDone message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.AgentTurnDone
             * @static
             * @param {fluent_audio.v1.AgentTurnDone} message AgentTurnDone
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            AgentTurnDone.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.sessionId = "";
                    object.userTurnId = "";
                    object.agentTurnId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    object.status = options.enums === String ? "AGENT_TURN_DONE_STATUS_UNSPECIFIED" : 0;
                }
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    object.userTurnId = message.userTurnId;
                if (message.agentTurnId != null && Object.hasOwnProperty.call(message, "agentTurnId"))
                    object.agentTurnId = message.agentTurnId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.status != null && Object.hasOwnProperty.call(message, "status"))
                    object.status = options.enums === String ? $root.fluent_audio.v1.AgentTurnDoneStatus[message.status] === undefined ? message.status : $root.fluent_audio.v1.AgentTurnDoneStatus[message.status] : message.status;
                if (message.reason != null && Object.hasOwnProperty.call(message, "reason")) {
                    object.reason = message.reason;
                    if (options.oneofs)
                        object._reason = "reason";
                }
                return object;
            };

            /**
             * Converts this AgentTurnDone to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.AgentTurnDone
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            AgentTurnDone.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for AgentTurnDone
             * @function getTypeUrl
             * @memberof fluent_audio.v1.AgentTurnDone
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            AgentTurnDone.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.AgentTurnDone";
            };

            return AgentTurnDone;
        })();

        v1.AgentApprovalRequest = (function() {

            /**
             * Properties of an AgentApprovalRequest.
             * @memberof fluent_audio.v1
             * @interface IAgentApprovalRequest
             * @property {string|null} [sessionId] AgentApprovalRequest sessionId
             * @property {string|null} [userTurnId] AgentApprovalRequest userTurnId
             * @property {string|null} [approvalId] AgentApprovalRequest approvalId
             * @property {number|Long|null} [seq] AgentApprovalRequest seq
             * @property {string|null} [prompt] AgentApprovalRequest prompt
             * @property {string|null} [actionLabel] AgentApprovalRequest actionLabel
             */

            /**
             * Constructs a new AgentApprovalRequest.
             * @memberof fluent_audio.v1
             * @classdesc Represents an AgentApprovalRequest.
             * @implements IAgentApprovalRequest
             * @constructor
             * @param {fluent_audio.v1.IAgentApprovalRequest=} [properties] Properties to set
             */
            function AgentApprovalRequest(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * AgentApprovalRequest sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.AgentApprovalRequest
             * @instance
             */
            AgentApprovalRequest.prototype.sessionId = "";

            /**
             * AgentApprovalRequest userTurnId.
             * @member {string} userTurnId
             * @memberof fluent_audio.v1.AgentApprovalRequest
             * @instance
             */
            AgentApprovalRequest.prototype.userTurnId = "";

            /**
             * AgentApprovalRequest approvalId.
             * @member {string} approvalId
             * @memberof fluent_audio.v1.AgentApprovalRequest
             * @instance
             */
            AgentApprovalRequest.prototype.approvalId = "";

            /**
             * AgentApprovalRequest seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.AgentApprovalRequest
             * @instance
             */
            AgentApprovalRequest.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * AgentApprovalRequest prompt.
             * @member {string} prompt
             * @memberof fluent_audio.v1.AgentApprovalRequest
             * @instance
             */
            AgentApprovalRequest.prototype.prompt = "";

            /**
             * AgentApprovalRequest actionLabel.
             * @member {string} actionLabel
             * @memberof fluent_audio.v1.AgentApprovalRequest
             * @instance
             */
            AgentApprovalRequest.prototype.actionLabel = "";

            /**
             * Creates a new AgentApprovalRequest instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.AgentApprovalRequest
             * @static
             * @param {fluent_audio.v1.IAgentApprovalRequest=} [properties] Properties to set
             * @returns {fluent_audio.v1.AgentApprovalRequest} AgentApprovalRequest instance
             */
            AgentApprovalRequest.create = function create(properties) {
                return new AgentApprovalRequest(properties);
            };

            /**
             * Encodes the specified AgentApprovalRequest message. Does not implicitly {@link fluent_audio.v1.AgentApprovalRequest.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.AgentApprovalRequest
             * @static
             * @param {fluent_audio.v1.IAgentApprovalRequest} message AgentApprovalRequest message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AgentApprovalRequest.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.sessionId);
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.userTurnId);
                if (message.approvalId != null && Object.hasOwnProperty.call(message, "approvalId"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.approvalId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.seq);
                if (message.prompt != null && Object.hasOwnProperty.call(message, "prompt"))
                    writer.uint32(/* id 5, wireType 2 =*/42).string(message.prompt);
                if (message.actionLabel != null && Object.hasOwnProperty.call(message, "actionLabel"))
                    writer.uint32(/* id 6, wireType 2 =*/50).string(message.actionLabel);
                return writer;
            };

            /**
             * Encodes the specified AgentApprovalRequest message, length delimited. Does not implicitly {@link fluent_audio.v1.AgentApprovalRequest.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.AgentApprovalRequest
             * @static
             * @param {fluent_audio.v1.IAgentApprovalRequest} message AgentApprovalRequest message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AgentApprovalRequest.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes an AgentApprovalRequest message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.AgentApprovalRequest
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.AgentApprovalRequest} AgentApprovalRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AgentApprovalRequest.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.AgentApprovalRequest();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 2: {
                            message.userTurnId = reader.string();
                            break;
                        }
                    case 3: {
                            message.approvalId = reader.string();
                            break;
                        }
                    case 4: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 5: {
                            message.prompt = reader.string();
                            break;
                        }
                    case 6: {
                            message.actionLabel = reader.string();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes an AgentApprovalRequest message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.AgentApprovalRequest
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.AgentApprovalRequest} AgentApprovalRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AgentApprovalRequest.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies an AgentApprovalRequest message.
             * @function verify
             * @memberof fluent_audio.v1.AgentApprovalRequest
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            AgentApprovalRequest.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    if (!$util.isString(message.userTurnId))
                        return "userTurnId: string expected";
                if (message.approvalId != null && Object.hasOwnProperty.call(message, "approvalId"))
                    if (!$util.isString(message.approvalId))
                        return "approvalId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.prompt != null && Object.hasOwnProperty.call(message, "prompt"))
                    if (!$util.isString(message.prompt))
                        return "prompt: string expected";
                if (message.actionLabel != null && Object.hasOwnProperty.call(message, "actionLabel"))
                    if (!$util.isString(message.actionLabel))
                        return "actionLabel: string expected";
                return null;
            };

            /**
             * Creates an AgentApprovalRequest message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.AgentApprovalRequest
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.AgentApprovalRequest} AgentApprovalRequest
             */
            AgentApprovalRequest.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.AgentApprovalRequest)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.AgentApprovalRequest: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.AgentApprovalRequest();
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.userTurnId != null)
                    message.userTurnId = String(object.userTurnId);
                if (object.approvalId != null)
                    message.approvalId = String(object.approvalId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.prompt != null)
                    message.prompt = String(object.prompt);
                if (object.actionLabel != null)
                    message.actionLabel = String(object.actionLabel);
                return message;
            };

            /**
             * Creates a plain object from an AgentApprovalRequest message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.AgentApprovalRequest
             * @static
             * @param {fluent_audio.v1.AgentApprovalRequest} message AgentApprovalRequest
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            AgentApprovalRequest.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.sessionId = "";
                    object.userTurnId = "";
                    object.approvalId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    object.prompt = "";
                    object.actionLabel = "";
                }
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    object.userTurnId = message.userTurnId;
                if (message.approvalId != null && Object.hasOwnProperty.call(message, "approvalId"))
                    object.approvalId = message.approvalId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.prompt != null && Object.hasOwnProperty.call(message, "prompt"))
                    object.prompt = message.prompt;
                if (message.actionLabel != null && Object.hasOwnProperty.call(message, "actionLabel"))
                    object.actionLabel = message.actionLabel;
                return object;
            };

            /**
             * Converts this AgentApprovalRequest to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.AgentApprovalRequest
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            AgentApprovalRequest.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for AgentApprovalRequest
             * @function getTypeUrl
             * @memberof fluent_audio.v1.AgentApprovalRequest
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            AgentApprovalRequest.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.AgentApprovalRequest";
            };

            return AgentApprovalRequest;
        })();

        v1.AgentApprovalResponse = (function() {

            /**
             * Properties of an AgentApprovalResponse.
             * @memberof fluent_audio.v1
             * @interface IAgentApprovalResponse
             * @property {string|null} [sessionId] AgentApprovalResponse sessionId
             * @property {string|null} [userTurnId] AgentApprovalResponse userTurnId
             * @property {string|null} [approvalId] AgentApprovalResponse approvalId
             * @property {number|Long|null} [seq] AgentApprovalResponse seq
             * @property {fluent_audio.v1.AgentApprovalDecision|null} [decision] AgentApprovalResponse decision
             * @property {fluent_audio.v1.AgentApprovalScope|null} [scope] AgentApprovalResponse scope
             * @property {string|null} [reason] AgentApprovalResponse reason
             */

            /**
             * Constructs a new AgentApprovalResponse.
             * @memberof fluent_audio.v1
             * @classdesc Represents an AgentApprovalResponse.
             * @implements IAgentApprovalResponse
             * @constructor
             * @param {fluent_audio.v1.IAgentApprovalResponse=} [properties] Properties to set
             */
            function AgentApprovalResponse(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * AgentApprovalResponse sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.AgentApprovalResponse
             * @instance
             */
            AgentApprovalResponse.prototype.sessionId = "";

            /**
             * AgentApprovalResponse userTurnId.
             * @member {string} userTurnId
             * @memberof fluent_audio.v1.AgentApprovalResponse
             * @instance
             */
            AgentApprovalResponse.prototype.userTurnId = "";

            /**
             * AgentApprovalResponse approvalId.
             * @member {string} approvalId
             * @memberof fluent_audio.v1.AgentApprovalResponse
             * @instance
             */
            AgentApprovalResponse.prototype.approvalId = "";

            /**
             * AgentApprovalResponse seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.AgentApprovalResponse
             * @instance
             */
            AgentApprovalResponse.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * AgentApprovalResponse decision.
             * @member {fluent_audio.v1.AgentApprovalDecision} decision
             * @memberof fluent_audio.v1.AgentApprovalResponse
             * @instance
             */
            AgentApprovalResponse.prototype.decision = 0;

            /**
             * AgentApprovalResponse scope.
             * @member {fluent_audio.v1.AgentApprovalScope} scope
             * @memberof fluent_audio.v1.AgentApprovalResponse
             * @instance
             */
            AgentApprovalResponse.prototype.scope = 0;

            /**
             * AgentApprovalResponse reason.
             * @member {string|null|undefined} reason
             * @memberof fluent_audio.v1.AgentApprovalResponse
             * @instance
             */
            AgentApprovalResponse.prototype.reason = null;

            // OneOf field names bound to virtual getters and setters
            var $oneOfFields;

            // Virtual OneOf for proto3 optional field
            Object.defineProperty(AgentApprovalResponse.prototype, "_reason", {
                get: $util.oneOfGetter($oneOfFields = ["reason"]),
                set: $util.oneOfSetter($oneOfFields)
            });

            /**
             * Creates a new AgentApprovalResponse instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.AgentApprovalResponse
             * @static
             * @param {fluent_audio.v1.IAgentApprovalResponse=} [properties] Properties to set
             * @returns {fluent_audio.v1.AgentApprovalResponse} AgentApprovalResponse instance
             */
            AgentApprovalResponse.create = function create(properties) {
                return new AgentApprovalResponse(properties);
            };

            /**
             * Encodes the specified AgentApprovalResponse message. Does not implicitly {@link fluent_audio.v1.AgentApprovalResponse.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.AgentApprovalResponse
             * @static
             * @param {fluent_audio.v1.IAgentApprovalResponse} message AgentApprovalResponse message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AgentApprovalResponse.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.sessionId);
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.userTurnId);
                if (message.approvalId != null && Object.hasOwnProperty.call(message, "approvalId"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.approvalId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.seq);
                if (message.decision != null && Object.hasOwnProperty.call(message, "decision"))
                    writer.uint32(/* id 5, wireType 0 =*/40).int32(message.decision);
                if (message.scope != null && Object.hasOwnProperty.call(message, "scope"))
                    writer.uint32(/* id 6, wireType 0 =*/48).int32(message.scope);
                if (message.reason != null && Object.hasOwnProperty.call(message, "reason"))
                    writer.uint32(/* id 7, wireType 2 =*/58).string(message.reason);
                return writer;
            };

            /**
             * Encodes the specified AgentApprovalResponse message, length delimited. Does not implicitly {@link fluent_audio.v1.AgentApprovalResponse.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.AgentApprovalResponse
             * @static
             * @param {fluent_audio.v1.IAgentApprovalResponse} message AgentApprovalResponse message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AgentApprovalResponse.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes an AgentApprovalResponse message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.AgentApprovalResponse
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.AgentApprovalResponse} AgentApprovalResponse
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AgentApprovalResponse.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.AgentApprovalResponse();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 2: {
                            message.userTurnId = reader.string();
                            break;
                        }
                    case 3: {
                            message.approvalId = reader.string();
                            break;
                        }
                    case 4: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 5: {
                            message.decision = reader.int32();
                            break;
                        }
                    case 6: {
                            message.scope = reader.int32();
                            break;
                        }
                    case 7: {
                            message.reason = reader.string();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes an AgentApprovalResponse message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.AgentApprovalResponse
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.AgentApprovalResponse} AgentApprovalResponse
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AgentApprovalResponse.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies an AgentApprovalResponse message.
             * @function verify
             * @memberof fluent_audio.v1.AgentApprovalResponse
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            AgentApprovalResponse.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                var properties = {};
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    if (!$util.isString(message.userTurnId))
                        return "userTurnId: string expected";
                if (message.approvalId != null && Object.hasOwnProperty.call(message, "approvalId"))
                    if (!$util.isString(message.approvalId))
                        return "approvalId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.decision != null && Object.hasOwnProperty.call(message, "decision"))
                    switch (message.decision) {
                    default:
                        return "decision: enum value expected";
                    case 0:
                    case 1:
                    case 2:
                    case 3:
                        break;
                    }
                if (message.scope != null && Object.hasOwnProperty.call(message, "scope"))
                    switch (message.scope) {
                    default:
                        return "scope: enum value expected";
                    case 0:
                    case 1:
                    case 2:
                        break;
                    }
                if (message.reason != null && Object.hasOwnProperty.call(message, "reason")) {
                    properties._reason = 1;
                    if (!$util.isString(message.reason))
                        return "reason: string expected";
                }
                return null;
            };

            /**
             * Creates an AgentApprovalResponse message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.AgentApprovalResponse
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.AgentApprovalResponse} AgentApprovalResponse
             */
            AgentApprovalResponse.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.AgentApprovalResponse)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.AgentApprovalResponse: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.AgentApprovalResponse();
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.userTurnId != null)
                    message.userTurnId = String(object.userTurnId);
                if (object.approvalId != null)
                    message.approvalId = String(object.approvalId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                switch (object.decision) {
                default:
                    if (typeof object.decision === "number") {
                        message.decision = object.decision;
                        break;
                    }
                    break;
                case "AGENT_APPROVAL_DECISION_UNSPECIFIED":
                case 0:
                    message.decision = 0;
                    break;
                case "AGENT_APPROVAL_DECISION_ACCEPT":
                case 1:
                    message.decision = 1;
                    break;
                case "AGENT_APPROVAL_DECISION_DECLINE":
                case 2:
                    message.decision = 2;
                    break;
                case "AGENT_APPROVAL_DECISION_CANCEL":
                case 3:
                    message.decision = 3;
                    break;
                }
                switch (object.scope) {
                default:
                    if (typeof object.scope === "number") {
                        message.scope = object.scope;
                        break;
                    }
                    break;
                case "AGENT_APPROVAL_SCOPE_UNSPECIFIED":
                case 0:
                    message.scope = 0;
                    break;
                case "AGENT_APPROVAL_SCOPE_TURN":
                case 1:
                    message.scope = 1;
                    break;
                case "AGENT_APPROVAL_SCOPE_SESSION":
                case 2:
                    message.scope = 2;
                    break;
                }
                if (object.reason != null)
                    message.reason = String(object.reason);
                return message;
            };

            /**
             * Creates a plain object from an AgentApprovalResponse message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.AgentApprovalResponse
             * @static
             * @param {fluent_audio.v1.AgentApprovalResponse} message AgentApprovalResponse
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            AgentApprovalResponse.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.sessionId = "";
                    object.userTurnId = "";
                    object.approvalId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    object.decision = options.enums === String ? "AGENT_APPROVAL_DECISION_UNSPECIFIED" : 0;
                    object.scope = options.enums === String ? "AGENT_APPROVAL_SCOPE_UNSPECIFIED" : 0;
                }
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    object.userTurnId = message.userTurnId;
                if (message.approvalId != null && Object.hasOwnProperty.call(message, "approvalId"))
                    object.approvalId = message.approvalId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.decision != null && Object.hasOwnProperty.call(message, "decision"))
                    object.decision = options.enums === String ? $root.fluent_audio.v1.AgentApprovalDecision[message.decision] === undefined ? message.decision : $root.fluent_audio.v1.AgentApprovalDecision[message.decision] : message.decision;
                if (message.scope != null && Object.hasOwnProperty.call(message, "scope"))
                    object.scope = options.enums === String ? $root.fluent_audio.v1.AgentApprovalScope[message.scope] === undefined ? message.scope : $root.fluent_audio.v1.AgentApprovalScope[message.scope] : message.scope;
                if (message.reason != null && Object.hasOwnProperty.call(message, "reason")) {
                    object.reason = message.reason;
                    if (options.oneofs)
                        object._reason = "reason";
                }
                return object;
            };

            /**
             * Converts this AgentApprovalResponse to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.AgentApprovalResponse
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            AgentApprovalResponse.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for AgentApprovalResponse
             * @function getTypeUrl
             * @memberof fluent_audio.v1.AgentApprovalResponse
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            AgentApprovalResponse.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.AgentApprovalResponse";
            };

            return AgentApprovalResponse;
        })();

        v1.AgentToolEvent = (function() {

            /**
             * Properties of an AgentToolEvent.
             * @memberof fluent_audio.v1
             * @interface IAgentToolEvent
             * @property {string|null} [sessionId] AgentToolEvent sessionId
             * @property {string|null} [userTurnId] AgentToolEvent userTurnId
             * @property {string|null} [toolCallId] AgentToolEvent toolCallId
             * @property {number|Long|null} [seq] AgentToolEvent seq
             * @property {fluent_audio.v1.AgentToolEventKind|null} [event] AgentToolEvent event
             * @property {string|null} [name] AgentToolEvent name
             * @property {string|null} [summary] AgentToolEvent summary
             * @property {string|null} [errorMessage] AgentToolEvent errorMessage
             */

            /**
             * Constructs a new AgentToolEvent.
             * @memberof fluent_audio.v1
             * @classdesc Represents an AgentToolEvent.
             * @implements IAgentToolEvent
             * @constructor
             * @param {fluent_audio.v1.IAgentToolEvent=} [properties] Properties to set
             */
            function AgentToolEvent(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * AgentToolEvent sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.AgentToolEvent
             * @instance
             */
            AgentToolEvent.prototype.sessionId = "";

            /**
             * AgentToolEvent userTurnId.
             * @member {string} userTurnId
             * @memberof fluent_audio.v1.AgentToolEvent
             * @instance
             */
            AgentToolEvent.prototype.userTurnId = "";

            /**
             * AgentToolEvent toolCallId.
             * @member {string} toolCallId
             * @memberof fluent_audio.v1.AgentToolEvent
             * @instance
             */
            AgentToolEvent.prototype.toolCallId = "";

            /**
             * AgentToolEvent seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.AgentToolEvent
             * @instance
             */
            AgentToolEvent.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * AgentToolEvent event.
             * @member {fluent_audio.v1.AgentToolEventKind} event
             * @memberof fluent_audio.v1.AgentToolEvent
             * @instance
             */
            AgentToolEvent.prototype.event = 0;

            /**
             * AgentToolEvent name.
             * @member {string} name
             * @memberof fluent_audio.v1.AgentToolEvent
             * @instance
             */
            AgentToolEvent.prototype.name = "";

            /**
             * AgentToolEvent summary.
             * @member {string|null|undefined} summary
             * @memberof fluent_audio.v1.AgentToolEvent
             * @instance
             */
            AgentToolEvent.prototype.summary = null;

            /**
             * AgentToolEvent errorMessage.
             * @member {string|null|undefined} errorMessage
             * @memberof fluent_audio.v1.AgentToolEvent
             * @instance
             */
            AgentToolEvent.prototype.errorMessage = null;

            // OneOf field names bound to virtual getters and setters
            var $oneOfFields;

            // Virtual OneOf for proto3 optional field
            Object.defineProperty(AgentToolEvent.prototype, "_summary", {
                get: $util.oneOfGetter($oneOfFields = ["summary"]),
                set: $util.oneOfSetter($oneOfFields)
            });

            // Virtual OneOf for proto3 optional field
            Object.defineProperty(AgentToolEvent.prototype, "_errorMessage", {
                get: $util.oneOfGetter($oneOfFields = ["errorMessage"]),
                set: $util.oneOfSetter($oneOfFields)
            });

            /**
             * Creates a new AgentToolEvent instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.AgentToolEvent
             * @static
             * @param {fluent_audio.v1.IAgentToolEvent=} [properties] Properties to set
             * @returns {fluent_audio.v1.AgentToolEvent} AgentToolEvent instance
             */
            AgentToolEvent.create = function create(properties) {
                return new AgentToolEvent(properties);
            };

            /**
             * Encodes the specified AgentToolEvent message. Does not implicitly {@link fluent_audio.v1.AgentToolEvent.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.AgentToolEvent
             * @static
             * @param {fluent_audio.v1.IAgentToolEvent} message AgentToolEvent message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AgentToolEvent.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.sessionId);
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.userTurnId);
                if (message.toolCallId != null && Object.hasOwnProperty.call(message, "toolCallId"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.toolCallId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.seq);
                if (message.event != null && Object.hasOwnProperty.call(message, "event"))
                    writer.uint32(/* id 5, wireType 0 =*/40).int32(message.event);
                if (message.name != null && Object.hasOwnProperty.call(message, "name"))
                    writer.uint32(/* id 6, wireType 2 =*/50).string(message.name);
                if (message.summary != null && Object.hasOwnProperty.call(message, "summary"))
                    writer.uint32(/* id 7, wireType 2 =*/58).string(message.summary);
                if (message.errorMessage != null && Object.hasOwnProperty.call(message, "errorMessage"))
                    writer.uint32(/* id 8, wireType 2 =*/66).string(message.errorMessage);
                return writer;
            };

            /**
             * Encodes the specified AgentToolEvent message, length delimited. Does not implicitly {@link fluent_audio.v1.AgentToolEvent.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.AgentToolEvent
             * @static
             * @param {fluent_audio.v1.IAgentToolEvent} message AgentToolEvent message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AgentToolEvent.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes an AgentToolEvent message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.AgentToolEvent
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.AgentToolEvent} AgentToolEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AgentToolEvent.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.AgentToolEvent();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 2: {
                            message.userTurnId = reader.string();
                            break;
                        }
                    case 3: {
                            message.toolCallId = reader.string();
                            break;
                        }
                    case 4: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 5: {
                            message.event = reader.int32();
                            break;
                        }
                    case 6: {
                            message.name = reader.string();
                            break;
                        }
                    case 7: {
                            message.summary = reader.string();
                            break;
                        }
                    case 8: {
                            message.errorMessage = reader.string();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes an AgentToolEvent message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.AgentToolEvent
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.AgentToolEvent} AgentToolEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AgentToolEvent.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies an AgentToolEvent message.
             * @function verify
             * @memberof fluent_audio.v1.AgentToolEvent
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            AgentToolEvent.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                var properties = {};
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    if (!$util.isString(message.userTurnId))
                        return "userTurnId: string expected";
                if (message.toolCallId != null && Object.hasOwnProperty.call(message, "toolCallId"))
                    if (!$util.isString(message.toolCallId))
                        return "toolCallId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.event != null && Object.hasOwnProperty.call(message, "event"))
                    switch (message.event) {
                    default:
                        return "event: enum value expected";
                    case 0:
                    case 1:
                    case 2:
                    case 3:
                        break;
                    }
                if (message.name != null && Object.hasOwnProperty.call(message, "name"))
                    if (!$util.isString(message.name))
                        return "name: string expected";
                if (message.summary != null && Object.hasOwnProperty.call(message, "summary")) {
                    properties._summary = 1;
                    if (!$util.isString(message.summary))
                        return "summary: string expected";
                }
                if (message.errorMessage != null && Object.hasOwnProperty.call(message, "errorMessage")) {
                    properties._errorMessage = 1;
                    if (!$util.isString(message.errorMessage))
                        return "errorMessage: string expected";
                }
                return null;
            };

            /**
             * Creates an AgentToolEvent message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.AgentToolEvent
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.AgentToolEvent} AgentToolEvent
             */
            AgentToolEvent.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.AgentToolEvent)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.AgentToolEvent: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.AgentToolEvent();
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.userTurnId != null)
                    message.userTurnId = String(object.userTurnId);
                if (object.toolCallId != null)
                    message.toolCallId = String(object.toolCallId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                switch (object.event) {
                default:
                    if (typeof object.event === "number") {
                        message.event = object.event;
                        break;
                    }
                    break;
                case "AGENT_TOOL_EVENT_KIND_UNSPECIFIED":
                case 0:
                    message.event = 0;
                    break;
                case "AGENT_TOOL_EVENT_KIND_STARTED":
                case 1:
                    message.event = 1;
                    break;
                case "AGENT_TOOL_EVENT_KIND_COMPLETED":
                case 2:
                    message.event = 2;
                    break;
                case "AGENT_TOOL_EVENT_KIND_FAILED":
                case 3:
                    message.event = 3;
                    break;
                }
                if (object.name != null)
                    message.name = String(object.name);
                if (object.summary != null)
                    message.summary = String(object.summary);
                if (object.errorMessage != null)
                    message.errorMessage = String(object.errorMessage);
                return message;
            };

            /**
             * Creates a plain object from an AgentToolEvent message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.AgentToolEvent
             * @static
             * @param {fluent_audio.v1.AgentToolEvent} message AgentToolEvent
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            AgentToolEvent.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.sessionId = "";
                    object.userTurnId = "";
                    object.toolCallId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    object.event = options.enums === String ? "AGENT_TOOL_EVENT_KIND_UNSPECIFIED" : 0;
                    object.name = "";
                }
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    object.userTurnId = message.userTurnId;
                if (message.toolCallId != null && Object.hasOwnProperty.call(message, "toolCallId"))
                    object.toolCallId = message.toolCallId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.event != null && Object.hasOwnProperty.call(message, "event"))
                    object.event = options.enums === String ? $root.fluent_audio.v1.AgentToolEventKind[message.event] === undefined ? message.event : $root.fluent_audio.v1.AgentToolEventKind[message.event] : message.event;
                if (message.name != null && Object.hasOwnProperty.call(message, "name"))
                    object.name = message.name;
                if (message.summary != null && Object.hasOwnProperty.call(message, "summary")) {
                    object.summary = message.summary;
                    if (options.oneofs)
                        object._summary = "summary";
                }
                if (message.errorMessage != null && Object.hasOwnProperty.call(message, "errorMessage")) {
                    object.errorMessage = message.errorMessage;
                    if (options.oneofs)
                        object._errorMessage = "errorMessage";
                }
                return object;
            };

            /**
             * Converts this AgentToolEvent to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.AgentToolEvent
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            AgentToolEvent.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for AgentToolEvent
             * @function getTypeUrl
             * @memberof fluent_audio.v1.AgentToolEvent
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            AgentToolEvent.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.AgentToolEvent";
            };

            return AgentToolEvent;
        })();

        v1.AgentCancelRequest = (function() {

            /**
             * Properties of an AgentCancelRequest.
             * @memberof fluent_audio.v1
             * @interface IAgentCancelRequest
             * @property {string|null} [sessionId] AgentCancelRequest sessionId
             * @property {string|null} [userTurnId] AgentCancelRequest userTurnId
             * @property {number|Long|null} [seq] AgentCancelRequest seq
             * @property {string|null} [reason] AgentCancelRequest reason
             */

            /**
             * Constructs a new AgentCancelRequest.
             * @memberof fluent_audio.v1
             * @classdesc Represents an AgentCancelRequest.
             * @implements IAgentCancelRequest
             * @constructor
             * @param {fluent_audio.v1.IAgentCancelRequest=} [properties] Properties to set
             */
            function AgentCancelRequest(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * AgentCancelRequest sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.AgentCancelRequest
             * @instance
             */
            AgentCancelRequest.prototype.sessionId = "";

            /**
             * AgentCancelRequest userTurnId.
             * @member {string} userTurnId
             * @memberof fluent_audio.v1.AgentCancelRequest
             * @instance
             */
            AgentCancelRequest.prototype.userTurnId = "";

            /**
             * AgentCancelRequest seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.AgentCancelRequest
             * @instance
             */
            AgentCancelRequest.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * AgentCancelRequest reason.
             * @member {string|null|undefined} reason
             * @memberof fluent_audio.v1.AgentCancelRequest
             * @instance
             */
            AgentCancelRequest.prototype.reason = null;

            // OneOf field names bound to virtual getters and setters
            var $oneOfFields;

            // Virtual OneOf for proto3 optional field
            Object.defineProperty(AgentCancelRequest.prototype, "_reason", {
                get: $util.oneOfGetter($oneOfFields = ["reason"]),
                set: $util.oneOfSetter($oneOfFields)
            });

            /**
             * Creates a new AgentCancelRequest instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.AgentCancelRequest
             * @static
             * @param {fluent_audio.v1.IAgentCancelRequest=} [properties] Properties to set
             * @returns {fluent_audio.v1.AgentCancelRequest} AgentCancelRequest instance
             */
            AgentCancelRequest.create = function create(properties) {
                return new AgentCancelRequest(properties);
            };

            /**
             * Encodes the specified AgentCancelRequest message. Does not implicitly {@link fluent_audio.v1.AgentCancelRequest.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.AgentCancelRequest
             * @static
             * @param {fluent_audio.v1.IAgentCancelRequest} message AgentCancelRequest message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AgentCancelRequest.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.sessionId);
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.userTurnId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 3, wireType 0 =*/24).uint64(message.seq);
                if (message.reason != null && Object.hasOwnProperty.call(message, "reason"))
                    writer.uint32(/* id 4, wireType 2 =*/34).string(message.reason);
                return writer;
            };

            /**
             * Encodes the specified AgentCancelRequest message, length delimited. Does not implicitly {@link fluent_audio.v1.AgentCancelRequest.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.AgentCancelRequest
             * @static
             * @param {fluent_audio.v1.IAgentCancelRequest} message AgentCancelRequest message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AgentCancelRequest.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes an AgentCancelRequest message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.AgentCancelRequest
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.AgentCancelRequest} AgentCancelRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AgentCancelRequest.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.AgentCancelRequest();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 2: {
                            message.userTurnId = reader.string();
                            break;
                        }
                    case 3: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 4: {
                            message.reason = reader.string();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes an AgentCancelRequest message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.AgentCancelRequest
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.AgentCancelRequest} AgentCancelRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AgentCancelRequest.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies an AgentCancelRequest message.
             * @function verify
             * @memberof fluent_audio.v1.AgentCancelRequest
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            AgentCancelRequest.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                var properties = {};
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    if (!$util.isString(message.userTurnId))
                        return "userTurnId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.reason != null && Object.hasOwnProperty.call(message, "reason")) {
                    properties._reason = 1;
                    if (!$util.isString(message.reason))
                        return "reason: string expected";
                }
                return null;
            };

            /**
             * Creates an AgentCancelRequest message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.AgentCancelRequest
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.AgentCancelRequest} AgentCancelRequest
             */
            AgentCancelRequest.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.AgentCancelRequest)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.AgentCancelRequest: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.AgentCancelRequest();
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.userTurnId != null)
                    message.userTurnId = String(object.userTurnId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.reason != null)
                    message.reason = String(object.reason);
                return message;
            };

            /**
             * Creates a plain object from an AgentCancelRequest message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.AgentCancelRequest
             * @static
             * @param {fluent_audio.v1.AgentCancelRequest} message AgentCancelRequest
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            AgentCancelRequest.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.sessionId = "";
                    object.userTurnId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                }
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    object.userTurnId = message.userTurnId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.reason != null && Object.hasOwnProperty.call(message, "reason")) {
                    object.reason = message.reason;
                    if (options.oneofs)
                        object._reason = "reason";
                }
                return object;
            };

            /**
             * Converts this AgentCancelRequest to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.AgentCancelRequest
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            AgentCancelRequest.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for AgentCancelRequest
             * @function getTypeUrl
             * @memberof fluent_audio.v1.AgentCancelRequest
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            AgentCancelRequest.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.AgentCancelRequest";
            };

            return AgentCancelRequest;
        })();

        v1.AgentUserInputOption = (function() {

            /**
             * Properties of an AgentUserInputOption.
             * @memberof fluent_audio.v1
             * @interface IAgentUserInputOption
             * @property {string|null} [label] AgentUserInputOption label
             * @property {string|null} [description] AgentUserInputOption description
             */

            /**
             * Constructs a new AgentUserInputOption.
             * @memberof fluent_audio.v1
             * @classdesc Represents an AgentUserInputOption.
             * @implements IAgentUserInputOption
             * @constructor
             * @param {fluent_audio.v1.IAgentUserInputOption=} [properties] Properties to set
             */
            function AgentUserInputOption(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * AgentUserInputOption label.
             * @member {string} label
             * @memberof fluent_audio.v1.AgentUserInputOption
             * @instance
             */
            AgentUserInputOption.prototype.label = "";

            /**
             * AgentUserInputOption description.
             * @member {string} description
             * @memberof fluent_audio.v1.AgentUserInputOption
             * @instance
             */
            AgentUserInputOption.prototype.description = "";

            /**
             * Creates a new AgentUserInputOption instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.AgentUserInputOption
             * @static
             * @param {fluent_audio.v1.IAgentUserInputOption=} [properties] Properties to set
             * @returns {fluent_audio.v1.AgentUserInputOption} AgentUserInputOption instance
             */
            AgentUserInputOption.create = function create(properties) {
                return new AgentUserInputOption(properties);
            };

            /**
             * Encodes the specified AgentUserInputOption message. Does not implicitly {@link fluent_audio.v1.AgentUserInputOption.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.AgentUserInputOption
             * @static
             * @param {fluent_audio.v1.IAgentUserInputOption} message AgentUserInputOption message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AgentUserInputOption.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.label != null && Object.hasOwnProperty.call(message, "label"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.label);
                if (message.description != null && Object.hasOwnProperty.call(message, "description"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.description);
                return writer;
            };

            /**
             * Encodes the specified AgentUserInputOption message, length delimited. Does not implicitly {@link fluent_audio.v1.AgentUserInputOption.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.AgentUserInputOption
             * @static
             * @param {fluent_audio.v1.IAgentUserInputOption} message AgentUserInputOption message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AgentUserInputOption.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes an AgentUserInputOption message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.AgentUserInputOption
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.AgentUserInputOption} AgentUserInputOption
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AgentUserInputOption.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.AgentUserInputOption();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.label = reader.string();
                            break;
                        }
                    case 2: {
                            message.description = reader.string();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes an AgentUserInputOption message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.AgentUserInputOption
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.AgentUserInputOption} AgentUserInputOption
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AgentUserInputOption.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies an AgentUserInputOption message.
             * @function verify
             * @memberof fluent_audio.v1.AgentUserInputOption
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            AgentUserInputOption.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.label != null && Object.hasOwnProperty.call(message, "label"))
                    if (!$util.isString(message.label))
                        return "label: string expected";
                if (message.description != null && Object.hasOwnProperty.call(message, "description"))
                    if (!$util.isString(message.description))
                        return "description: string expected";
                return null;
            };

            /**
             * Creates an AgentUserInputOption message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.AgentUserInputOption
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.AgentUserInputOption} AgentUserInputOption
             */
            AgentUserInputOption.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.AgentUserInputOption)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.AgentUserInputOption: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.AgentUserInputOption();
                if (object.label != null)
                    message.label = String(object.label);
                if (object.description != null)
                    message.description = String(object.description);
                return message;
            };

            /**
             * Creates a plain object from an AgentUserInputOption message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.AgentUserInputOption
             * @static
             * @param {fluent_audio.v1.AgentUserInputOption} message AgentUserInputOption
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            AgentUserInputOption.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.label = "";
                    object.description = "";
                }
                if (message.label != null && Object.hasOwnProperty.call(message, "label"))
                    object.label = message.label;
                if (message.description != null && Object.hasOwnProperty.call(message, "description"))
                    object.description = message.description;
                return object;
            };

            /**
             * Converts this AgentUserInputOption to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.AgentUserInputOption
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            AgentUserInputOption.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for AgentUserInputOption
             * @function getTypeUrl
             * @memberof fluent_audio.v1.AgentUserInputOption
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            AgentUserInputOption.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.AgentUserInputOption";
            };

            return AgentUserInputOption;
        })();

        v1.AgentUserInputQuestion = (function() {

            /**
             * Properties of an AgentUserInputQuestion.
             * @memberof fluent_audio.v1
             * @interface IAgentUserInputQuestion
             * @property {string|null} [id] AgentUserInputQuestion id
             * @property {string|null} [header] AgentUserInputQuestion header
             * @property {string|null} [question] AgentUserInputQuestion question
             * @property {boolean|null} [isOther] AgentUserInputQuestion isOther
             * @property {boolean|null} [isSecret] AgentUserInputQuestion isSecret
             * @property {Array.<fluent_audio.v1.IAgentUserInputOption>|null} [options] AgentUserInputQuestion options
             */

            /**
             * Constructs a new AgentUserInputQuestion.
             * @memberof fluent_audio.v1
             * @classdesc Represents an AgentUserInputQuestion.
             * @implements IAgentUserInputQuestion
             * @constructor
             * @param {fluent_audio.v1.IAgentUserInputQuestion=} [properties] Properties to set
             */
            function AgentUserInputQuestion(properties) {
                this.options = [];
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * AgentUserInputQuestion id.
             * @member {string} id
             * @memberof fluent_audio.v1.AgentUserInputQuestion
             * @instance
             */
            AgentUserInputQuestion.prototype.id = "";

            /**
             * AgentUserInputQuestion header.
             * @member {string} header
             * @memberof fluent_audio.v1.AgentUserInputQuestion
             * @instance
             */
            AgentUserInputQuestion.prototype.header = "";

            /**
             * AgentUserInputQuestion question.
             * @member {string} question
             * @memberof fluent_audio.v1.AgentUserInputQuestion
             * @instance
             */
            AgentUserInputQuestion.prototype.question = "";

            /**
             * AgentUserInputQuestion isOther.
             * @member {boolean} isOther
             * @memberof fluent_audio.v1.AgentUserInputQuestion
             * @instance
             */
            AgentUserInputQuestion.prototype.isOther = false;

            /**
             * AgentUserInputQuestion isSecret.
             * @member {boolean} isSecret
             * @memberof fluent_audio.v1.AgentUserInputQuestion
             * @instance
             */
            AgentUserInputQuestion.prototype.isSecret = false;

            /**
             * AgentUserInputQuestion options.
             * @member {Array.<fluent_audio.v1.IAgentUserInputOption>} options
             * @memberof fluent_audio.v1.AgentUserInputQuestion
             * @instance
             */
            AgentUserInputQuestion.prototype.options = $util.emptyArray;

            /**
             * Creates a new AgentUserInputQuestion instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.AgentUserInputQuestion
             * @static
             * @param {fluent_audio.v1.IAgentUserInputQuestion=} [properties] Properties to set
             * @returns {fluent_audio.v1.AgentUserInputQuestion} AgentUserInputQuestion instance
             */
            AgentUserInputQuestion.create = function create(properties) {
                return new AgentUserInputQuestion(properties);
            };

            /**
             * Encodes the specified AgentUserInputQuestion message. Does not implicitly {@link fluent_audio.v1.AgentUserInputQuestion.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.AgentUserInputQuestion
             * @static
             * @param {fluent_audio.v1.IAgentUserInputQuestion} message AgentUserInputQuestion message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AgentUserInputQuestion.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.id != null && Object.hasOwnProperty.call(message, "id"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.id);
                if (message.header != null && Object.hasOwnProperty.call(message, "header"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.header);
                if (message.question != null && Object.hasOwnProperty.call(message, "question"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.question);
                if (message.isOther != null && Object.hasOwnProperty.call(message, "isOther"))
                    writer.uint32(/* id 4, wireType 0 =*/32).bool(message.isOther);
                if (message.isSecret != null && Object.hasOwnProperty.call(message, "isSecret"))
                    writer.uint32(/* id 5, wireType 0 =*/40).bool(message.isSecret);
                if (message.options != null && message.options.length)
                    for (var i = 0; i < message.options.length; ++i)
                        $root.fluent_audio.v1.AgentUserInputOption.encode(message.options[i], writer.uint32(/* id 6, wireType 2 =*/50).fork(), q + 1).ldelim();
                return writer;
            };

            /**
             * Encodes the specified AgentUserInputQuestion message, length delimited. Does not implicitly {@link fluent_audio.v1.AgentUserInputQuestion.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.AgentUserInputQuestion
             * @static
             * @param {fluent_audio.v1.IAgentUserInputQuestion} message AgentUserInputQuestion message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AgentUserInputQuestion.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes an AgentUserInputQuestion message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.AgentUserInputQuestion
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.AgentUserInputQuestion} AgentUserInputQuestion
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AgentUserInputQuestion.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.AgentUserInputQuestion();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.id = reader.string();
                            break;
                        }
                    case 2: {
                            message.header = reader.string();
                            break;
                        }
                    case 3: {
                            message.question = reader.string();
                            break;
                        }
                    case 4: {
                            message.isOther = reader.bool();
                            break;
                        }
                    case 5: {
                            message.isSecret = reader.bool();
                            break;
                        }
                    case 6: {
                            if (!(message.options && message.options.length))
                                message.options = [];
                            message.options.push($root.fluent_audio.v1.AgentUserInputOption.decode(reader, reader.uint32(), undefined, long + 1));
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes an AgentUserInputQuestion message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.AgentUserInputQuestion
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.AgentUserInputQuestion} AgentUserInputQuestion
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AgentUserInputQuestion.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies an AgentUserInputQuestion message.
             * @function verify
             * @memberof fluent_audio.v1.AgentUserInputQuestion
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            AgentUserInputQuestion.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.id != null && Object.hasOwnProperty.call(message, "id"))
                    if (!$util.isString(message.id))
                        return "id: string expected";
                if (message.header != null && Object.hasOwnProperty.call(message, "header"))
                    if (!$util.isString(message.header))
                        return "header: string expected";
                if (message.question != null && Object.hasOwnProperty.call(message, "question"))
                    if (!$util.isString(message.question))
                        return "question: string expected";
                if (message.isOther != null && Object.hasOwnProperty.call(message, "isOther"))
                    if (typeof message.isOther !== "boolean")
                        return "isOther: boolean expected";
                if (message.isSecret != null && Object.hasOwnProperty.call(message, "isSecret"))
                    if (typeof message.isSecret !== "boolean")
                        return "isSecret: boolean expected";
                if (message.options != null && Object.hasOwnProperty.call(message, "options")) {
                    if (!Array.isArray(message.options))
                        return "options: array expected";
                    for (var i = 0; i < message.options.length; ++i) {
                        var error = $root.fluent_audio.v1.AgentUserInputOption.verify(message.options[i], long + 1);
                        if (error)
                            return "options." + error;
                    }
                }
                return null;
            };

            /**
             * Creates an AgentUserInputQuestion message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.AgentUserInputQuestion
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.AgentUserInputQuestion} AgentUserInputQuestion
             */
            AgentUserInputQuestion.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.AgentUserInputQuestion)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.AgentUserInputQuestion: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.AgentUserInputQuestion();
                if (object.id != null)
                    message.id = String(object.id);
                if (object.header != null)
                    message.header = String(object.header);
                if (object.question != null)
                    message.question = String(object.question);
                if (object.isOther != null)
                    message.isOther = Boolean(object.isOther);
                if (object.isSecret != null)
                    message.isSecret = Boolean(object.isSecret);
                if (object.options) {
                    if (!Array.isArray(object.options))
                        throw TypeError(".fluent_audio.v1.AgentUserInputQuestion.options: array expected");
                    message.options = [];
                    for (var i = 0; i < object.options.length; ++i) {
                        if (!$util.isObject(object.options[i]))
                            throw TypeError(".fluent_audio.v1.AgentUserInputQuestion.options: object expected");
                        message.options[i] = $root.fluent_audio.v1.AgentUserInputOption.fromObject(object.options[i], long + 1);
                    }
                }
                return message;
            };

            /**
             * Creates a plain object from an AgentUserInputQuestion message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.AgentUserInputQuestion
             * @static
             * @param {fluent_audio.v1.AgentUserInputQuestion} message AgentUserInputQuestion
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            AgentUserInputQuestion.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.arrays || options.defaults)
                    object.options = [];
                if (options.defaults) {
                    object.id = "";
                    object.header = "";
                    object.question = "";
                    object.isOther = false;
                    object.isSecret = false;
                }
                if (message.id != null && Object.hasOwnProperty.call(message, "id"))
                    object.id = message.id;
                if (message.header != null && Object.hasOwnProperty.call(message, "header"))
                    object.header = message.header;
                if (message.question != null && Object.hasOwnProperty.call(message, "question"))
                    object.question = message.question;
                if (message.isOther != null && Object.hasOwnProperty.call(message, "isOther"))
                    object.isOther = message.isOther;
                if (message.isSecret != null && Object.hasOwnProperty.call(message, "isSecret"))
                    object.isSecret = message.isSecret;
                if (message.options && message.options.length) {
                    object.options = [];
                    for (var j = 0; j < message.options.length; ++j)
                        object.options[j] = $root.fluent_audio.v1.AgentUserInputOption.toObject(message.options[j], options, q + 1);
                }
                return object;
            };

            /**
             * Converts this AgentUserInputQuestion to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.AgentUserInputQuestion
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            AgentUserInputQuestion.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for AgentUserInputQuestion
             * @function getTypeUrl
             * @memberof fluent_audio.v1.AgentUserInputQuestion
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            AgentUserInputQuestion.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.AgentUserInputQuestion";
            };

            return AgentUserInputQuestion;
        })();

        v1.AgentUserInputRequest = (function() {

            /**
             * Properties of an AgentUserInputRequest.
             * @memberof fluent_audio.v1
             * @interface IAgentUserInputRequest
             * @property {string|null} [sessionId] AgentUserInputRequest sessionId
             * @property {string|null} [userTurnId] AgentUserInputRequest userTurnId
             * @property {string|null} [requestId] AgentUserInputRequest requestId
             * @property {number|Long|null} [seq] AgentUserInputRequest seq
             * @property {Array.<fluent_audio.v1.IAgentUserInputQuestion>|null} [questions] AgentUserInputRequest questions
             */

            /**
             * Constructs a new AgentUserInputRequest.
             * @memberof fluent_audio.v1
             * @classdesc Represents an AgentUserInputRequest.
             * @implements IAgentUserInputRequest
             * @constructor
             * @param {fluent_audio.v1.IAgentUserInputRequest=} [properties] Properties to set
             */
            function AgentUserInputRequest(properties) {
                this.questions = [];
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * AgentUserInputRequest sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.AgentUserInputRequest
             * @instance
             */
            AgentUserInputRequest.prototype.sessionId = "";

            /**
             * AgentUserInputRequest userTurnId.
             * @member {string} userTurnId
             * @memberof fluent_audio.v1.AgentUserInputRequest
             * @instance
             */
            AgentUserInputRequest.prototype.userTurnId = "";

            /**
             * AgentUserInputRequest requestId.
             * @member {string} requestId
             * @memberof fluent_audio.v1.AgentUserInputRequest
             * @instance
             */
            AgentUserInputRequest.prototype.requestId = "";

            /**
             * AgentUserInputRequest seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.AgentUserInputRequest
             * @instance
             */
            AgentUserInputRequest.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * AgentUserInputRequest questions.
             * @member {Array.<fluent_audio.v1.IAgentUserInputQuestion>} questions
             * @memberof fluent_audio.v1.AgentUserInputRequest
             * @instance
             */
            AgentUserInputRequest.prototype.questions = $util.emptyArray;

            /**
             * Creates a new AgentUserInputRequest instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.AgentUserInputRequest
             * @static
             * @param {fluent_audio.v1.IAgentUserInputRequest=} [properties] Properties to set
             * @returns {fluent_audio.v1.AgentUserInputRequest} AgentUserInputRequest instance
             */
            AgentUserInputRequest.create = function create(properties) {
                return new AgentUserInputRequest(properties);
            };

            /**
             * Encodes the specified AgentUserInputRequest message. Does not implicitly {@link fluent_audio.v1.AgentUserInputRequest.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.AgentUserInputRequest
             * @static
             * @param {fluent_audio.v1.IAgentUserInputRequest} message AgentUserInputRequest message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AgentUserInputRequest.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.sessionId);
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.userTurnId);
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.requestId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.seq);
                if (message.questions != null && message.questions.length)
                    for (var i = 0; i < message.questions.length; ++i)
                        $root.fluent_audio.v1.AgentUserInputQuestion.encode(message.questions[i], writer.uint32(/* id 5, wireType 2 =*/42).fork(), q + 1).ldelim();
                return writer;
            };

            /**
             * Encodes the specified AgentUserInputRequest message, length delimited. Does not implicitly {@link fluent_audio.v1.AgentUserInputRequest.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.AgentUserInputRequest
             * @static
             * @param {fluent_audio.v1.IAgentUserInputRequest} message AgentUserInputRequest message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AgentUserInputRequest.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes an AgentUserInputRequest message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.AgentUserInputRequest
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.AgentUserInputRequest} AgentUserInputRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AgentUserInputRequest.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.AgentUserInputRequest();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 2: {
                            message.userTurnId = reader.string();
                            break;
                        }
                    case 3: {
                            message.requestId = reader.string();
                            break;
                        }
                    case 4: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 5: {
                            if (!(message.questions && message.questions.length))
                                message.questions = [];
                            message.questions.push($root.fluent_audio.v1.AgentUserInputQuestion.decode(reader, reader.uint32(), undefined, long + 1));
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes an AgentUserInputRequest message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.AgentUserInputRequest
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.AgentUserInputRequest} AgentUserInputRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AgentUserInputRequest.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies an AgentUserInputRequest message.
             * @function verify
             * @memberof fluent_audio.v1.AgentUserInputRequest
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            AgentUserInputRequest.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    if (!$util.isString(message.userTurnId))
                        return "userTurnId: string expected";
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    if (!$util.isString(message.requestId))
                        return "requestId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.questions != null && Object.hasOwnProperty.call(message, "questions")) {
                    if (!Array.isArray(message.questions))
                        return "questions: array expected";
                    for (var i = 0; i < message.questions.length; ++i) {
                        var error = $root.fluent_audio.v1.AgentUserInputQuestion.verify(message.questions[i], long + 1);
                        if (error)
                            return "questions." + error;
                    }
                }
                return null;
            };

            /**
             * Creates an AgentUserInputRequest message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.AgentUserInputRequest
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.AgentUserInputRequest} AgentUserInputRequest
             */
            AgentUserInputRequest.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.AgentUserInputRequest)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.AgentUserInputRequest: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.AgentUserInputRequest();
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.userTurnId != null)
                    message.userTurnId = String(object.userTurnId);
                if (object.requestId != null)
                    message.requestId = String(object.requestId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.questions) {
                    if (!Array.isArray(object.questions))
                        throw TypeError(".fluent_audio.v1.AgentUserInputRequest.questions: array expected");
                    message.questions = [];
                    for (var i = 0; i < object.questions.length; ++i) {
                        if (!$util.isObject(object.questions[i]))
                            throw TypeError(".fluent_audio.v1.AgentUserInputRequest.questions: object expected");
                        message.questions[i] = $root.fluent_audio.v1.AgentUserInputQuestion.fromObject(object.questions[i], long + 1);
                    }
                }
                return message;
            };

            /**
             * Creates a plain object from an AgentUserInputRequest message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.AgentUserInputRequest
             * @static
             * @param {fluent_audio.v1.AgentUserInputRequest} message AgentUserInputRequest
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            AgentUserInputRequest.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.arrays || options.defaults)
                    object.questions = [];
                if (options.defaults) {
                    object.sessionId = "";
                    object.userTurnId = "";
                    object.requestId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                }
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    object.userTurnId = message.userTurnId;
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    object.requestId = message.requestId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.questions && message.questions.length) {
                    object.questions = [];
                    for (var j = 0; j < message.questions.length; ++j)
                        object.questions[j] = $root.fluent_audio.v1.AgentUserInputQuestion.toObject(message.questions[j], options, q + 1);
                }
                return object;
            };

            /**
             * Converts this AgentUserInputRequest to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.AgentUserInputRequest
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            AgentUserInputRequest.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for AgentUserInputRequest
             * @function getTypeUrl
             * @memberof fluent_audio.v1.AgentUserInputRequest
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            AgentUserInputRequest.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.AgentUserInputRequest";
            };

            return AgentUserInputRequest;
        })();

        v1.AgentUserInputAnswer = (function() {

            /**
             * Properties of an AgentUserInputAnswer.
             * @memberof fluent_audio.v1
             * @interface IAgentUserInputAnswer
             * @property {string|null} [questionId] AgentUserInputAnswer questionId
             * @property {Array.<string>|null} [answers] AgentUserInputAnswer answers
             */

            /**
             * Constructs a new AgentUserInputAnswer.
             * @memberof fluent_audio.v1
             * @classdesc Represents an AgentUserInputAnswer.
             * @implements IAgentUserInputAnswer
             * @constructor
             * @param {fluent_audio.v1.IAgentUserInputAnswer=} [properties] Properties to set
             */
            function AgentUserInputAnswer(properties) {
                this.answers = [];
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * AgentUserInputAnswer questionId.
             * @member {string} questionId
             * @memberof fluent_audio.v1.AgentUserInputAnswer
             * @instance
             */
            AgentUserInputAnswer.prototype.questionId = "";

            /**
             * AgentUserInputAnswer answers.
             * @member {Array.<string>} answers
             * @memberof fluent_audio.v1.AgentUserInputAnswer
             * @instance
             */
            AgentUserInputAnswer.prototype.answers = $util.emptyArray;

            /**
             * Creates a new AgentUserInputAnswer instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.AgentUserInputAnswer
             * @static
             * @param {fluent_audio.v1.IAgentUserInputAnswer=} [properties] Properties to set
             * @returns {fluent_audio.v1.AgentUserInputAnswer} AgentUserInputAnswer instance
             */
            AgentUserInputAnswer.create = function create(properties) {
                return new AgentUserInputAnswer(properties);
            };

            /**
             * Encodes the specified AgentUserInputAnswer message. Does not implicitly {@link fluent_audio.v1.AgentUserInputAnswer.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.AgentUserInputAnswer
             * @static
             * @param {fluent_audio.v1.IAgentUserInputAnswer} message AgentUserInputAnswer message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AgentUserInputAnswer.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.questionId != null && Object.hasOwnProperty.call(message, "questionId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.questionId);
                if (message.answers != null && message.answers.length)
                    for (var i = 0; i < message.answers.length; ++i)
                        writer.uint32(/* id 2, wireType 2 =*/18).string(message.answers[i]);
                return writer;
            };

            /**
             * Encodes the specified AgentUserInputAnswer message, length delimited. Does not implicitly {@link fluent_audio.v1.AgentUserInputAnswer.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.AgentUserInputAnswer
             * @static
             * @param {fluent_audio.v1.IAgentUserInputAnswer} message AgentUserInputAnswer message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AgentUserInputAnswer.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes an AgentUserInputAnswer message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.AgentUserInputAnswer
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.AgentUserInputAnswer} AgentUserInputAnswer
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AgentUserInputAnswer.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.AgentUserInputAnswer();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.questionId = reader.string();
                            break;
                        }
                    case 2: {
                            if (!(message.answers && message.answers.length))
                                message.answers = [];
                            message.answers.push(reader.string());
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes an AgentUserInputAnswer message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.AgentUserInputAnswer
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.AgentUserInputAnswer} AgentUserInputAnswer
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AgentUserInputAnswer.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies an AgentUserInputAnswer message.
             * @function verify
             * @memberof fluent_audio.v1.AgentUserInputAnswer
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            AgentUserInputAnswer.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.questionId != null && Object.hasOwnProperty.call(message, "questionId"))
                    if (!$util.isString(message.questionId))
                        return "questionId: string expected";
                if (message.answers != null && Object.hasOwnProperty.call(message, "answers")) {
                    if (!Array.isArray(message.answers))
                        return "answers: array expected";
                    for (var i = 0; i < message.answers.length; ++i)
                        if (!$util.isString(message.answers[i]))
                            return "answers: string[] expected";
                }
                return null;
            };

            /**
             * Creates an AgentUserInputAnswer message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.AgentUserInputAnswer
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.AgentUserInputAnswer} AgentUserInputAnswer
             */
            AgentUserInputAnswer.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.AgentUserInputAnswer)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.AgentUserInputAnswer: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.AgentUserInputAnswer();
                if (object.questionId != null)
                    message.questionId = String(object.questionId);
                if (object.answers) {
                    if (!Array.isArray(object.answers))
                        throw TypeError(".fluent_audio.v1.AgentUserInputAnswer.answers: array expected");
                    message.answers = [];
                    for (var i = 0; i < object.answers.length; ++i)
                        message.answers[i] = String(object.answers[i]);
                }
                return message;
            };

            /**
             * Creates a plain object from an AgentUserInputAnswer message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.AgentUserInputAnswer
             * @static
             * @param {fluent_audio.v1.AgentUserInputAnswer} message AgentUserInputAnswer
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            AgentUserInputAnswer.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.arrays || options.defaults)
                    object.answers = [];
                if (options.defaults)
                    object.questionId = "";
                if (message.questionId != null && Object.hasOwnProperty.call(message, "questionId"))
                    object.questionId = message.questionId;
                if (message.answers && message.answers.length) {
                    object.answers = [];
                    for (var j = 0; j < message.answers.length; ++j)
                        object.answers[j] = message.answers[j];
                }
                return object;
            };

            /**
             * Converts this AgentUserInputAnswer to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.AgentUserInputAnswer
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            AgentUserInputAnswer.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for AgentUserInputAnswer
             * @function getTypeUrl
             * @memberof fluent_audio.v1.AgentUserInputAnswer
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            AgentUserInputAnswer.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.AgentUserInputAnswer";
            };

            return AgentUserInputAnswer;
        })();

        v1.AgentUserInputResponse = (function() {

            /**
             * Properties of an AgentUserInputResponse.
             * @memberof fluent_audio.v1
             * @interface IAgentUserInputResponse
             * @property {string|null} [sessionId] AgentUserInputResponse sessionId
             * @property {string|null} [userTurnId] AgentUserInputResponse userTurnId
             * @property {string|null} [requestId] AgentUserInputResponse requestId
             * @property {number|Long|null} [seq] AgentUserInputResponse seq
             * @property {Array.<fluent_audio.v1.IAgentUserInputAnswer>|null} [answers] AgentUserInputResponse answers
             */

            /**
             * Constructs a new AgentUserInputResponse.
             * @memberof fluent_audio.v1
             * @classdesc Represents an AgentUserInputResponse.
             * @implements IAgentUserInputResponse
             * @constructor
             * @param {fluent_audio.v1.IAgentUserInputResponse=} [properties] Properties to set
             */
            function AgentUserInputResponse(properties) {
                this.answers = [];
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * AgentUserInputResponse sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.AgentUserInputResponse
             * @instance
             */
            AgentUserInputResponse.prototype.sessionId = "";

            /**
             * AgentUserInputResponse userTurnId.
             * @member {string} userTurnId
             * @memberof fluent_audio.v1.AgentUserInputResponse
             * @instance
             */
            AgentUserInputResponse.prototype.userTurnId = "";

            /**
             * AgentUserInputResponse requestId.
             * @member {string} requestId
             * @memberof fluent_audio.v1.AgentUserInputResponse
             * @instance
             */
            AgentUserInputResponse.prototype.requestId = "";

            /**
             * AgentUserInputResponse seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.AgentUserInputResponse
             * @instance
             */
            AgentUserInputResponse.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * AgentUserInputResponse answers.
             * @member {Array.<fluent_audio.v1.IAgentUserInputAnswer>} answers
             * @memberof fluent_audio.v1.AgentUserInputResponse
             * @instance
             */
            AgentUserInputResponse.prototype.answers = $util.emptyArray;

            /**
             * Creates a new AgentUserInputResponse instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.AgentUserInputResponse
             * @static
             * @param {fluent_audio.v1.IAgentUserInputResponse=} [properties] Properties to set
             * @returns {fluent_audio.v1.AgentUserInputResponse} AgentUserInputResponse instance
             */
            AgentUserInputResponse.create = function create(properties) {
                return new AgentUserInputResponse(properties);
            };

            /**
             * Encodes the specified AgentUserInputResponse message. Does not implicitly {@link fluent_audio.v1.AgentUserInputResponse.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.AgentUserInputResponse
             * @static
             * @param {fluent_audio.v1.IAgentUserInputResponse} message AgentUserInputResponse message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AgentUserInputResponse.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.sessionId);
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.userTurnId);
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.requestId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.seq);
                if (message.answers != null && message.answers.length)
                    for (var i = 0; i < message.answers.length; ++i)
                        $root.fluent_audio.v1.AgentUserInputAnswer.encode(message.answers[i], writer.uint32(/* id 5, wireType 2 =*/42).fork(), q + 1).ldelim();
                return writer;
            };

            /**
             * Encodes the specified AgentUserInputResponse message, length delimited. Does not implicitly {@link fluent_audio.v1.AgentUserInputResponse.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.AgentUserInputResponse
             * @static
             * @param {fluent_audio.v1.IAgentUserInputResponse} message AgentUserInputResponse message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AgentUserInputResponse.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes an AgentUserInputResponse message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.AgentUserInputResponse
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.AgentUserInputResponse} AgentUserInputResponse
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AgentUserInputResponse.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.AgentUserInputResponse();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 2: {
                            message.userTurnId = reader.string();
                            break;
                        }
                    case 3: {
                            message.requestId = reader.string();
                            break;
                        }
                    case 4: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 5: {
                            if (!(message.answers && message.answers.length))
                                message.answers = [];
                            message.answers.push($root.fluent_audio.v1.AgentUserInputAnswer.decode(reader, reader.uint32(), undefined, long + 1));
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes an AgentUserInputResponse message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.AgentUserInputResponse
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.AgentUserInputResponse} AgentUserInputResponse
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AgentUserInputResponse.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies an AgentUserInputResponse message.
             * @function verify
             * @memberof fluent_audio.v1.AgentUserInputResponse
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            AgentUserInputResponse.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    if (!$util.isString(message.userTurnId))
                        return "userTurnId: string expected";
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    if (!$util.isString(message.requestId))
                        return "requestId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.answers != null && Object.hasOwnProperty.call(message, "answers")) {
                    if (!Array.isArray(message.answers))
                        return "answers: array expected";
                    for (var i = 0; i < message.answers.length; ++i) {
                        var error = $root.fluent_audio.v1.AgentUserInputAnswer.verify(message.answers[i], long + 1);
                        if (error)
                            return "answers." + error;
                    }
                }
                return null;
            };

            /**
             * Creates an AgentUserInputResponse message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.AgentUserInputResponse
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.AgentUserInputResponse} AgentUserInputResponse
             */
            AgentUserInputResponse.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.AgentUserInputResponse)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.AgentUserInputResponse: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.AgentUserInputResponse();
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.userTurnId != null)
                    message.userTurnId = String(object.userTurnId);
                if (object.requestId != null)
                    message.requestId = String(object.requestId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.answers) {
                    if (!Array.isArray(object.answers))
                        throw TypeError(".fluent_audio.v1.AgentUserInputResponse.answers: array expected");
                    message.answers = [];
                    for (var i = 0; i < object.answers.length; ++i) {
                        if (!$util.isObject(object.answers[i]))
                            throw TypeError(".fluent_audio.v1.AgentUserInputResponse.answers: object expected");
                        message.answers[i] = $root.fluent_audio.v1.AgentUserInputAnswer.fromObject(object.answers[i], long + 1);
                    }
                }
                return message;
            };

            /**
             * Creates a plain object from an AgentUserInputResponse message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.AgentUserInputResponse
             * @static
             * @param {fluent_audio.v1.AgentUserInputResponse} message AgentUserInputResponse
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            AgentUserInputResponse.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.arrays || options.defaults)
                    object.answers = [];
                if (options.defaults) {
                    object.sessionId = "";
                    object.userTurnId = "";
                    object.requestId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                }
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    object.userTurnId = message.userTurnId;
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    object.requestId = message.requestId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.answers && message.answers.length) {
                    object.answers = [];
                    for (var j = 0; j < message.answers.length; ++j)
                        object.answers[j] = $root.fluent_audio.v1.AgentUserInputAnswer.toObject(message.answers[j], options, q + 1);
                }
                return object;
            };

            /**
             * Converts this AgentUserInputResponse to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.AgentUserInputResponse
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            AgentUserInputResponse.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for AgentUserInputResponse
             * @function getTypeUrl
             * @memberof fluent_audio.v1.AgentUserInputResponse
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            AgentUserInputResponse.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.AgentUserInputResponse";
            };

            return AgentUserInputResponse;
        })();

        /**
         * AgentMcpElicitationMode enum.
         * @name fluent_audio.v1.AgentMcpElicitationMode
         * @enum {number}
         * @property {number} AGENT_MCP_ELICITATION_MODE_UNSPECIFIED=0 AGENT_MCP_ELICITATION_MODE_UNSPECIFIED value
         * @property {number} AGENT_MCP_ELICITATION_MODE_FORM=1 AGENT_MCP_ELICITATION_MODE_FORM value
         * @property {number} AGENT_MCP_ELICITATION_MODE_URL=2 AGENT_MCP_ELICITATION_MODE_URL value
         */
        v1.AgentMcpElicitationMode = (function() {
            var valuesById = {}, values = Object.create(valuesById);
            values[valuesById[0] = "AGENT_MCP_ELICITATION_MODE_UNSPECIFIED"] = 0;
            values[valuesById[1] = "AGENT_MCP_ELICITATION_MODE_FORM"] = 1;
            values[valuesById[2] = "AGENT_MCP_ELICITATION_MODE_URL"] = 2;
            return values;
        })();

        /**
         * AgentMcpElicitationAction enum.
         * @name fluent_audio.v1.AgentMcpElicitationAction
         * @enum {number}
         * @property {number} AGENT_MCP_ELICITATION_ACTION_UNSPECIFIED=0 AGENT_MCP_ELICITATION_ACTION_UNSPECIFIED value
         * @property {number} AGENT_MCP_ELICITATION_ACTION_ACCEPT=1 AGENT_MCP_ELICITATION_ACTION_ACCEPT value
         * @property {number} AGENT_MCP_ELICITATION_ACTION_DECLINE=2 AGENT_MCP_ELICITATION_ACTION_DECLINE value
         * @property {number} AGENT_MCP_ELICITATION_ACTION_CANCEL=3 AGENT_MCP_ELICITATION_ACTION_CANCEL value
         */
        v1.AgentMcpElicitationAction = (function() {
            var valuesById = {}, values = Object.create(valuesById);
            values[valuesById[0] = "AGENT_MCP_ELICITATION_ACTION_UNSPECIFIED"] = 0;
            values[valuesById[1] = "AGENT_MCP_ELICITATION_ACTION_ACCEPT"] = 1;
            values[valuesById[2] = "AGENT_MCP_ELICITATION_ACTION_DECLINE"] = 2;
            values[valuesById[3] = "AGENT_MCP_ELICITATION_ACTION_CANCEL"] = 3;
            return values;
        })();

        v1.AgentMcpElicitationRequest = (function() {

            /**
             * Properties of an AgentMcpElicitationRequest.
             * @memberof fluent_audio.v1
             * @interface IAgentMcpElicitationRequest
             * @property {string|null} [sessionId] AgentMcpElicitationRequest sessionId
             * @property {string|null} [userTurnId] AgentMcpElicitationRequest userTurnId
             * @property {string|null} [requestId] AgentMcpElicitationRequest requestId
             * @property {number|Long|null} [seq] AgentMcpElicitationRequest seq
             * @property {string|null} [serverName] AgentMcpElicitationRequest serverName
             * @property {fluent_audio.v1.AgentMcpElicitationMode|null} [mode] AgentMcpElicitationRequest mode
             * @property {string|null} [message] AgentMcpElicitationRequest message
             * @property {string|null} [url] AgentMcpElicitationRequest url
             * @property {string|null} [elicitationId] AgentMcpElicitationRequest elicitationId
             * @property {google.protobuf.IValue|null} [requestedSchema] AgentMcpElicitationRequest requestedSchema
             * @property {google.protobuf.IValue|null} [meta] AgentMcpElicitationRequest meta
             */

            /**
             * Constructs a new AgentMcpElicitationRequest.
             * @memberof fluent_audio.v1
             * @classdesc Represents an AgentMcpElicitationRequest.
             * @implements IAgentMcpElicitationRequest
             * @constructor
             * @param {fluent_audio.v1.IAgentMcpElicitationRequest=} [properties] Properties to set
             */
            function AgentMcpElicitationRequest(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * AgentMcpElicitationRequest sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.AgentMcpElicitationRequest
             * @instance
             */
            AgentMcpElicitationRequest.prototype.sessionId = "";

            /**
             * AgentMcpElicitationRequest userTurnId.
             * @member {string} userTurnId
             * @memberof fluent_audio.v1.AgentMcpElicitationRequest
             * @instance
             */
            AgentMcpElicitationRequest.prototype.userTurnId = "";

            /**
             * AgentMcpElicitationRequest requestId.
             * @member {string} requestId
             * @memberof fluent_audio.v1.AgentMcpElicitationRequest
             * @instance
             */
            AgentMcpElicitationRequest.prototype.requestId = "";

            /**
             * AgentMcpElicitationRequest seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.AgentMcpElicitationRequest
             * @instance
             */
            AgentMcpElicitationRequest.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * AgentMcpElicitationRequest serverName.
             * @member {string} serverName
             * @memberof fluent_audio.v1.AgentMcpElicitationRequest
             * @instance
             */
            AgentMcpElicitationRequest.prototype.serverName = "";

            /**
             * AgentMcpElicitationRequest mode.
             * @member {fluent_audio.v1.AgentMcpElicitationMode} mode
             * @memberof fluent_audio.v1.AgentMcpElicitationRequest
             * @instance
             */
            AgentMcpElicitationRequest.prototype.mode = 0;

            /**
             * AgentMcpElicitationRequest message.
             * @member {string} message
             * @memberof fluent_audio.v1.AgentMcpElicitationRequest
             * @instance
             */
            AgentMcpElicitationRequest.prototype.message = "";

            /**
             * AgentMcpElicitationRequest url.
             * @member {string|null|undefined} url
             * @memberof fluent_audio.v1.AgentMcpElicitationRequest
             * @instance
             */
            AgentMcpElicitationRequest.prototype.url = null;

            /**
             * AgentMcpElicitationRequest elicitationId.
             * @member {string|null|undefined} elicitationId
             * @memberof fluent_audio.v1.AgentMcpElicitationRequest
             * @instance
             */
            AgentMcpElicitationRequest.prototype.elicitationId = null;

            /**
             * AgentMcpElicitationRequest requestedSchema.
             * @member {google.protobuf.IValue|null|undefined} requestedSchema
             * @memberof fluent_audio.v1.AgentMcpElicitationRequest
             * @instance
             */
            AgentMcpElicitationRequest.prototype.requestedSchema = null;

            /**
             * AgentMcpElicitationRequest meta.
             * @member {google.protobuf.IValue|null|undefined} meta
             * @memberof fluent_audio.v1.AgentMcpElicitationRequest
             * @instance
             */
            AgentMcpElicitationRequest.prototype.meta = null;

            // OneOf field names bound to virtual getters and setters
            var $oneOfFields;

            // Virtual OneOf for proto3 optional field
            Object.defineProperty(AgentMcpElicitationRequest.prototype, "_url", {
                get: $util.oneOfGetter($oneOfFields = ["url"]),
                set: $util.oneOfSetter($oneOfFields)
            });

            // Virtual OneOf for proto3 optional field
            Object.defineProperty(AgentMcpElicitationRequest.prototype, "_elicitationId", {
                get: $util.oneOfGetter($oneOfFields = ["elicitationId"]),
                set: $util.oneOfSetter($oneOfFields)
            });

            // Virtual OneOf for proto3 optional field
            Object.defineProperty(AgentMcpElicitationRequest.prototype, "_requestedSchema", {
                get: $util.oneOfGetter($oneOfFields = ["requestedSchema"]),
                set: $util.oneOfSetter($oneOfFields)
            });

            // Virtual OneOf for proto3 optional field
            Object.defineProperty(AgentMcpElicitationRequest.prototype, "_meta", {
                get: $util.oneOfGetter($oneOfFields = ["meta"]),
                set: $util.oneOfSetter($oneOfFields)
            });

            /**
             * Creates a new AgentMcpElicitationRequest instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.AgentMcpElicitationRequest
             * @static
             * @param {fluent_audio.v1.IAgentMcpElicitationRequest=} [properties] Properties to set
             * @returns {fluent_audio.v1.AgentMcpElicitationRequest} AgentMcpElicitationRequest instance
             */
            AgentMcpElicitationRequest.create = function create(properties) {
                return new AgentMcpElicitationRequest(properties);
            };

            /**
             * Encodes the specified AgentMcpElicitationRequest message. Does not implicitly {@link fluent_audio.v1.AgentMcpElicitationRequest.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.AgentMcpElicitationRequest
             * @static
             * @param {fluent_audio.v1.IAgentMcpElicitationRequest} message AgentMcpElicitationRequest message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AgentMcpElicitationRequest.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.sessionId);
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.userTurnId);
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.requestId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.seq);
                if (message.serverName != null && Object.hasOwnProperty.call(message, "serverName"))
                    writer.uint32(/* id 5, wireType 2 =*/42).string(message.serverName);
                if (message.mode != null && Object.hasOwnProperty.call(message, "mode"))
                    writer.uint32(/* id 6, wireType 0 =*/48).int32(message.mode);
                if (message.message != null && Object.hasOwnProperty.call(message, "message"))
                    writer.uint32(/* id 7, wireType 2 =*/58).string(message.message);
                if (message.url != null && Object.hasOwnProperty.call(message, "url"))
                    writer.uint32(/* id 8, wireType 2 =*/66).string(message.url);
                if (message.elicitationId != null && Object.hasOwnProperty.call(message, "elicitationId"))
                    writer.uint32(/* id 9, wireType 2 =*/74).string(message.elicitationId);
                if (message.requestedSchema != null && Object.hasOwnProperty.call(message, "requestedSchema"))
                    $root.google.protobuf.Value.encode(message.requestedSchema, writer.uint32(/* id 10, wireType 2 =*/82).fork(), q + 1).ldelim();
                if (message.meta != null && Object.hasOwnProperty.call(message, "meta"))
                    $root.google.protobuf.Value.encode(message.meta, writer.uint32(/* id 11, wireType 2 =*/90).fork(), q + 1).ldelim();
                return writer;
            };

            /**
             * Encodes the specified AgentMcpElicitationRequest message, length delimited. Does not implicitly {@link fluent_audio.v1.AgentMcpElicitationRequest.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.AgentMcpElicitationRequest
             * @static
             * @param {fluent_audio.v1.IAgentMcpElicitationRequest} message AgentMcpElicitationRequest message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AgentMcpElicitationRequest.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes an AgentMcpElicitationRequest message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.AgentMcpElicitationRequest
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.AgentMcpElicitationRequest} AgentMcpElicitationRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AgentMcpElicitationRequest.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.AgentMcpElicitationRequest();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 2: {
                            message.userTurnId = reader.string();
                            break;
                        }
                    case 3: {
                            message.requestId = reader.string();
                            break;
                        }
                    case 4: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 5: {
                            message.serverName = reader.string();
                            break;
                        }
                    case 6: {
                            message.mode = reader.int32();
                            break;
                        }
                    case 7: {
                            message.message = reader.string();
                            break;
                        }
                    case 8: {
                            message.url = reader.string();
                            break;
                        }
                    case 9: {
                            message.elicitationId = reader.string();
                            break;
                        }
                    case 10: {
                            message.requestedSchema = $root.google.protobuf.Value.decode(reader, reader.uint32(), undefined, long + 1);
                            break;
                        }
                    case 11: {
                            message.meta = $root.google.protobuf.Value.decode(reader, reader.uint32(), undefined, long + 1);
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes an AgentMcpElicitationRequest message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.AgentMcpElicitationRequest
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.AgentMcpElicitationRequest} AgentMcpElicitationRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AgentMcpElicitationRequest.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies an AgentMcpElicitationRequest message.
             * @function verify
             * @memberof fluent_audio.v1.AgentMcpElicitationRequest
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            AgentMcpElicitationRequest.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                var properties = {};
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    if (!$util.isString(message.userTurnId))
                        return "userTurnId: string expected";
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    if (!$util.isString(message.requestId))
                        return "requestId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.serverName != null && Object.hasOwnProperty.call(message, "serverName"))
                    if (!$util.isString(message.serverName))
                        return "serverName: string expected";
                if (message.mode != null && Object.hasOwnProperty.call(message, "mode"))
                    switch (message.mode) {
                    default:
                        return "mode: enum value expected";
                    case 0:
                    case 1:
                    case 2:
                        break;
                    }
                if (message.message != null && Object.hasOwnProperty.call(message, "message"))
                    if (!$util.isString(message.message))
                        return "message: string expected";
                if (message.url != null && Object.hasOwnProperty.call(message, "url")) {
                    properties._url = 1;
                    if (!$util.isString(message.url))
                        return "url: string expected";
                }
                if (message.elicitationId != null && Object.hasOwnProperty.call(message, "elicitationId")) {
                    properties._elicitationId = 1;
                    if (!$util.isString(message.elicitationId))
                        return "elicitationId: string expected";
                }
                if (message.requestedSchema != null && Object.hasOwnProperty.call(message, "requestedSchema")) {
                    properties._requestedSchema = 1;
                    {
                        var error = $root.google.protobuf.Value.verify(message.requestedSchema, long + 1);
                        if (error)
                            return "requestedSchema." + error;
                    }
                }
                if (message.meta != null && Object.hasOwnProperty.call(message, "meta")) {
                    properties._meta = 1;
                    {
                        var error = $root.google.protobuf.Value.verify(message.meta, long + 1);
                        if (error)
                            return "meta." + error;
                    }
                }
                return null;
            };

            /**
             * Creates an AgentMcpElicitationRequest message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.AgentMcpElicitationRequest
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.AgentMcpElicitationRequest} AgentMcpElicitationRequest
             */
            AgentMcpElicitationRequest.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.AgentMcpElicitationRequest)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.AgentMcpElicitationRequest: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.AgentMcpElicitationRequest();
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.userTurnId != null)
                    message.userTurnId = String(object.userTurnId);
                if (object.requestId != null)
                    message.requestId = String(object.requestId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.serverName != null)
                    message.serverName = String(object.serverName);
                switch (object.mode) {
                default:
                    if (typeof object.mode === "number") {
                        message.mode = object.mode;
                        break;
                    }
                    break;
                case "AGENT_MCP_ELICITATION_MODE_UNSPECIFIED":
                case 0:
                    message.mode = 0;
                    break;
                case "AGENT_MCP_ELICITATION_MODE_FORM":
                case 1:
                    message.mode = 1;
                    break;
                case "AGENT_MCP_ELICITATION_MODE_URL":
                case 2:
                    message.mode = 2;
                    break;
                }
                if (object.message != null)
                    message.message = String(object.message);
                if (object.url != null)
                    message.url = String(object.url);
                if (object.elicitationId != null)
                    message.elicitationId = String(object.elicitationId);
                if (object.requestedSchema != null) {
                    if (!$util.isObject(object.requestedSchema))
                        throw TypeError(".fluent_audio.v1.AgentMcpElicitationRequest.requestedSchema: object expected");
                    message.requestedSchema = $root.google.protobuf.Value.fromObject(object.requestedSchema, long + 1);
                }
                if (object.meta != null) {
                    if (!$util.isObject(object.meta))
                        throw TypeError(".fluent_audio.v1.AgentMcpElicitationRequest.meta: object expected");
                    message.meta = $root.google.protobuf.Value.fromObject(object.meta, long + 1);
                }
                return message;
            };

            /**
             * Creates a plain object from an AgentMcpElicitationRequest message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.AgentMcpElicitationRequest
             * @static
             * @param {fluent_audio.v1.AgentMcpElicitationRequest} message AgentMcpElicitationRequest
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            AgentMcpElicitationRequest.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.sessionId = "";
                    object.userTurnId = "";
                    object.requestId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    object.serverName = "";
                    object.mode = options.enums === String ? "AGENT_MCP_ELICITATION_MODE_UNSPECIFIED" : 0;
                    object.message = "";
                }
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    object.userTurnId = message.userTurnId;
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    object.requestId = message.requestId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.serverName != null && Object.hasOwnProperty.call(message, "serverName"))
                    object.serverName = message.serverName;
                if (message.mode != null && Object.hasOwnProperty.call(message, "mode"))
                    object.mode = options.enums === String ? $root.fluent_audio.v1.AgentMcpElicitationMode[message.mode] === undefined ? message.mode : $root.fluent_audio.v1.AgentMcpElicitationMode[message.mode] : message.mode;
                if (message.message != null && Object.hasOwnProperty.call(message, "message"))
                    object.message = message.message;
                if (message.url != null && Object.hasOwnProperty.call(message, "url")) {
                    object.url = message.url;
                    if (options.oneofs)
                        object._url = "url";
                }
                if (message.elicitationId != null && Object.hasOwnProperty.call(message, "elicitationId")) {
                    object.elicitationId = message.elicitationId;
                    if (options.oneofs)
                        object._elicitationId = "elicitationId";
                }
                if (message.requestedSchema != null && Object.hasOwnProperty.call(message, "requestedSchema")) {
                    object.requestedSchema = $root.google.protobuf.Value.toObject(message.requestedSchema, options, q + 1);
                    if (options.oneofs)
                        object._requestedSchema = "requestedSchema";
                }
                if (message.meta != null && Object.hasOwnProperty.call(message, "meta")) {
                    object.meta = $root.google.protobuf.Value.toObject(message.meta, options, q + 1);
                    if (options.oneofs)
                        object._meta = "meta";
                }
                return object;
            };

            /**
             * Converts this AgentMcpElicitationRequest to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.AgentMcpElicitationRequest
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            AgentMcpElicitationRequest.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for AgentMcpElicitationRequest
             * @function getTypeUrl
             * @memberof fluent_audio.v1.AgentMcpElicitationRequest
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            AgentMcpElicitationRequest.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.AgentMcpElicitationRequest";
            };

            return AgentMcpElicitationRequest;
        })();

        v1.AgentMcpElicitationResponse = (function() {

            /**
             * Properties of an AgentMcpElicitationResponse.
             * @memberof fluent_audio.v1
             * @interface IAgentMcpElicitationResponse
             * @property {string|null} [sessionId] AgentMcpElicitationResponse sessionId
             * @property {string|null} [userTurnId] AgentMcpElicitationResponse userTurnId
             * @property {string|null} [requestId] AgentMcpElicitationResponse requestId
             * @property {number|Long|null} [seq] AgentMcpElicitationResponse seq
             * @property {fluent_audio.v1.AgentMcpElicitationAction|null} [action] AgentMcpElicitationResponse action
             * @property {google.protobuf.IValue|null} [content] AgentMcpElicitationResponse content
             * @property {google.protobuf.IValue|null} [meta] AgentMcpElicitationResponse meta
             */

            /**
             * Constructs a new AgentMcpElicitationResponse.
             * @memberof fluent_audio.v1
             * @classdesc Represents an AgentMcpElicitationResponse.
             * @implements IAgentMcpElicitationResponse
             * @constructor
             * @param {fluent_audio.v1.IAgentMcpElicitationResponse=} [properties] Properties to set
             */
            function AgentMcpElicitationResponse(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * AgentMcpElicitationResponse sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.AgentMcpElicitationResponse
             * @instance
             */
            AgentMcpElicitationResponse.prototype.sessionId = "";

            /**
             * AgentMcpElicitationResponse userTurnId.
             * @member {string} userTurnId
             * @memberof fluent_audio.v1.AgentMcpElicitationResponse
             * @instance
             */
            AgentMcpElicitationResponse.prototype.userTurnId = "";

            /**
             * AgentMcpElicitationResponse requestId.
             * @member {string} requestId
             * @memberof fluent_audio.v1.AgentMcpElicitationResponse
             * @instance
             */
            AgentMcpElicitationResponse.prototype.requestId = "";

            /**
             * AgentMcpElicitationResponse seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.AgentMcpElicitationResponse
             * @instance
             */
            AgentMcpElicitationResponse.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * AgentMcpElicitationResponse action.
             * @member {fluent_audio.v1.AgentMcpElicitationAction} action
             * @memberof fluent_audio.v1.AgentMcpElicitationResponse
             * @instance
             */
            AgentMcpElicitationResponse.prototype.action = 0;

            /**
             * AgentMcpElicitationResponse content.
             * @member {google.protobuf.IValue|null|undefined} content
             * @memberof fluent_audio.v1.AgentMcpElicitationResponse
             * @instance
             */
            AgentMcpElicitationResponse.prototype.content = null;

            /**
             * AgentMcpElicitationResponse meta.
             * @member {google.protobuf.IValue|null|undefined} meta
             * @memberof fluent_audio.v1.AgentMcpElicitationResponse
             * @instance
             */
            AgentMcpElicitationResponse.prototype.meta = null;

            // OneOf field names bound to virtual getters and setters
            var $oneOfFields;

            // Virtual OneOf for proto3 optional field
            Object.defineProperty(AgentMcpElicitationResponse.prototype, "_content", {
                get: $util.oneOfGetter($oneOfFields = ["content"]),
                set: $util.oneOfSetter($oneOfFields)
            });

            // Virtual OneOf for proto3 optional field
            Object.defineProperty(AgentMcpElicitationResponse.prototype, "_meta", {
                get: $util.oneOfGetter($oneOfFields = ["meta"]),
                set: $util.oneOfSetter($oneOfFields)
            });

            /**
             * Creates a new AgentMcpElicitationResponse instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.AgentMcpElicitationResponse
             * @static
             * @param {fluent_audio.v1.IAgentMcpElicitationResponse=} [properties] Properties to set
             * @returns {fluent_audio.v1.AgentMcpElicitationResponse} AgentMcpElicitationResponse instance
             */
            AgentMcpElicitationResponse.create = function create(properties) {
                return new AgentMcpElicitationResponse(properties);
            };

            /**
             * Encodes the specified AgentMcpElicitationResponse message. Does not implicitly {@link fluent_audio.v1.AgentMcpElicitationResponse.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.AgentMcpElicitationResponse
             * @static
             * @param {fluent_audio.v1.IAgentMcpElicitationResponse} message AgentMcpElicitationResponse message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AgentMcpElicitationResponse.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.sessionId);
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.userTurnId);
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.requestId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.seq);
                if (message.action != null && Object.hasOwnProperty.call(message, "action"))
                    writer.uint32(/* id 5, wireType 0 =*/40).int32(message.action);
                if (message.content != null && Object.hasOwnProperty.call(message, "content"))
                    $root.google.protobuf.Value.encode(message.content, writer.uint32(/* id 6, wireType 2 =*/50).fork(), q + 1).ldelim();
                if (message.meta != null && Object.hasOwnProperty.call(message, "meta"))
                    $root.google.protobuf.Value.encode(message.meta, writer.uint32(/* id 7, wireType 2 =*/58).fork(), q + 1).ldelim();
                return writer;
            };

            /**
             * Encodes the specified AgentMcpElicitationResponse message, length delimited. Does not implicitly {@link fluent_audio.v1.AgentMcpElicitationResponse.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.AgentMcpElicitationResponse
             * @static
             * @param {fluent_audio.v1.IAgentMcpElicitationResponse} message AgentMcpElicitationResponse message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            AgentMcpElicitationResponse.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes an AgentMcpElicitationResponse message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.AgentMcpElicitationResponse
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.AgentMcpElicitationResponse} AgentMcpElicitationResponse
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AgentMcpElicitationResponse.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.AgentMcpElicitationResponse();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 2: {
                            message.userTurnId = reader.string();
                            break;
                        }
                    case 3: {
                            message.requestId = reader.string();
                            break;
                        }
                    case 4: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 5: {
                            message.action = reader.int32();
                            break;
                        }
                    case 6: {
                            message.content = $root.google.protobuf.Value.decode(reader, reader.uint32(), undefined, long + 1);
                            break;
                        }
                    case 7: {
                            message.meta = $root.google.protobuf.Value.decode(reader, reader.uint32(), undefined, long + 1);
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes an AgentMcpElicitationResponse message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.AgentMcpElicitationResponse
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.AgentMcpElicitationResponse} AgentMcpElicitationResponse
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            AgentMcpElicitationResponse.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies an AgentMcpElicitationResponse message.
             * @function verify
             * @memberof fluent_audio.v1.AgentMcpElicitationResponse
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            AgentMcpElicitationResponse.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                var properties = {};
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    if (!$util.isString(message.userTurnId))
                        return "userTurnId: string expected";
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    if (!$util.isString(message.requestId))
                        return "requestId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.action != null && Object.hasOwnProperty.call(message, "action"))
                    switch (message.action) {
                    default:
                        return "action: enum value expected";
                    case 0:
                    case 1:
                    case 2:
                    case 3:
                        break;
                    }
                if (message.content != null && Object.hasOwnProperty.call(message, "content")) {
                    properties._content = 1;
                    {
                        var error = $root.google.protobuf.Value.verify(message.content, long + 1);
                        if (error)
                            return "content." + error;
                    }
                }
                if (message.meta != null && Object.hasOwnProperty.call(message, "meta")) {
                    properties._meta = 1;
                    {
                        var error = $root.google.protobuf.Value.verify(message.meta, long + 1);
                        if (error)
                            return "meta." + error;
                    }
                }
                return null;
            };

            /**
             * Creates an AgentMcpElicitationResponse message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.AgentMcpElicitationResponse
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.AgentMcpElicitationResponse} AgentMcpElicitationResponse
             */
            AgentMcpElicitationResponse.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.AgentMcpElicitationResponse)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.AgentMcpElicitationResponse: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.AgentMcpElicitationResponse();
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.userTurnId != null)
                    message.userTurnId = String(object.userTurnId);
                if (object.requestId != null)
                    message.requestId = String(object.requestId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                switch (object.action) {
                default:
                    if (typeof object.action === "number") {
                        message.action = object.action;
                        break;
                    }
                    break;
                case "AGENT_MCP_ELICITATION_ACTION_UNSPECIFIED":
                case 0:
                    message.action = 0;
                    break;
                case "AGENT_MCP_ELICITATION_ACTION_ACCEPT":
                case 1:
                    message.action = 1;
                    break;
                case "AGENT_MCP_ELICITATION_ACTION_DECLINE":
                case 2:
                    message.action = 2;
                    break;
                case "AGENT_MCP_ELICITATION_ACTION_CANCEL":
                case 3:
                    message.action = 3;
                    break;
                }
                if (object.content != null) {
                    if (!$util.isObject(object.content))
                        throw TypeError(".fluent_audio.v1.AgentMcpElicitationResponse.content: object expected");
                    message.content = $root.google.protobuf.Value.fromObject(object.content, long + 1);
                }
                if (object.meta != null) {
                    if (!$util.isObject(object.meta))
                        throw TypeError(".fluent_audio.v1.AgentMcpElicitationResponse.meta: object expected");
                    message.meta = $root.google.protobuf.Value.fromObject(object.meta, long + 1);
                }
                return message;
            };

            /**
             * Creates a plain object from an AgentMcpElicitationResponse message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.AgentMcpElicitationResponse
             * @static
             * @param {fluent_audio.v1.AgentMcpElicitationResponse} message AgentMcpElicitationResponse
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            AgentMcpElicitationResponse.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.sessionId = "";
                    object.userTurnId = "";
                    object.requestId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    object.action = options.enums === String ? "AGENT_MCP_ELICITATION_ACTION_UNSPECIFIED" : 0;
                }
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    object.userTurnId = message.userTurnId;
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    object.requestId = message.requestId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.action != null && Object.hasOwnProperty.call(message, "action"))
                    object.action = options.enums === String ? $root.fluent_audio.v1.AgentMcpElicitationAction[message.action] === undefined ? message.action : $root.fluent_audio.v1.AgentMcpElicitationAction[message.action] : message.action;
                if (message.content != null && Object.hasOwnProperty.call(message, "content")) {
                    object.content = $root.google.protobuf.Value.toObject(message.content, options, q + 1);
                    if (options.oneofs)
                        object._content = "content";
                }
                if (message.meta != null && Object.hasOwnProperty.call(message, "meta")) {
                    object.meta = $root.google.protobuf.Value.toObject(message.meta, options, q + 1);
                    if (options.oneofs)
                        object._meta = "meta";
                }
                return object;
            };

            /**
             * Converts this AgentMcpElicitationResponse to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.AgentMcpElicitationResponse
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            AgentMcpElicitationResponse.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for AgentMcpElicitationResponse
             * @function getTypeUrl
             * @memberof fluent_audio.v1.AgentMcpElicitationResponse
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            AgentMcpElicitationResponse.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.AgentMcpElicitationResponse";
            };

            return AgentMcpElicitationResponse;
        })();

        v1.TtsTextChunk = (function() {

            /**
             * Properties of a TtsTextChunk.
             * @memberof fluent_audio.v1
             * @interface ITtsTextChunk
             * @property {string|null} [requestId] TtsTextChunk requestId
             * @property {string|null} [sessionId] TtsTextChunk sessionId
             * @property {string|null} [userTurnId] TtsTextChunk userTurnId
             * @property {string|null} [assistantTurnId] TtsTextChunk assistantTurnId
             * @property {number|Long|null} [seq] TtsTextChunk seq
             * @property {string|null} [text] TtsTextChunk text
             * @property {boolean|null} [isFinal] TtsTextChunk isFinal
             */

            /**
             * Constructs a new TtsTextChunk.
             * @memberof fluent_audio.v1
             * @classdesc Represents a TtsTextChunk.
             * @implements ITtsTextChunk
             * @constructor
             * @param {fluent_audio.v1.ITtsTextChunk=} [properties] Properties to set
             */
            function TtsTextChunk(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * TtsTextChunk requestId.
             * @member {string} requestId
             * @memberof fluent_audio.v1.TtsTextChunk
             * @instance
             */
            TtsTextChunk.prototype.requestId = "";

            /**
             * TtsTextChunk sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.TtsTextChunk
             * @instance
             */
            TtsTextChunk.prototype.sessionId = "";

            /**
             * TtsTextChunk userTurnId.
             * @member {string} userTurnId
             * @memberof fluent_audio.v1.TtsTextChunk
             * @instance
             */
            TtsTextChunk.prototype.userTurnId = "";

            /**
             * TtsTextChunk assistantTurnId.
             * @member {string} assistantTurnId
             * @memberof fluent_audio.v1.TtsTextChunk
             * @instance
             */
            TtsTextChunk.prototype.assistantTurnId = "";

            /**
             * TtsTextChunk seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.TtsTextChunk
             * @instance
             */
            TtsTextChunk.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * TtsTextChunk text.
             * @member {string} text
             * @memberof fluent_audio.v1.TtsTextChunk
             * @instance
             */
            TtsTextChunk.prototype.text = "";

            /**
             * TtsTextChunk isFinal.
             * @member {boolean} isFinal
             * @memberof fluent_audio.v1.TtsTextChunk
             * @instance
             */
            TtsTextChunk.prototype.isFinal = false;

            /**
             * Creates a new TtsTextChunk instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.TtsTextChunk
             * @static
             * @param {fluent_audio.v1.ITtsTextChunk=} [properties] Properties to set
             * @returns {fluent_audio.v1.TtsTextChunk} TtsTextChunk instance
             */
            TtsTextChunk.create = function create(properties) {
                return new TtsTextChunk(properties);
            };

            /**
             * Encodes the specified TtsTextChunk message. Does not implicitly {@link fluent_audio.v1.TtsTextChunk.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.TtsTextChunk
             * @static
             * @param {fluent_audio.v1.ITtsTextChunk} message TtsTextChunk message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            TtsTextChunk.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.requestId);
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.sessionId);
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.userTurnId);
                if (message.assistantTurnId != null && Object.hasOwnProperty.call(message, "assistantTurnId"))
                    writer.uint32(/* id 4, wireType 2 =*/34).string(message.assistantTurnId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 5, wireType 0 =*/40).uint64(message.seq);
                if (message.text != null && Object.hasOwnProperty.call(message, "text"))
                    writer.uint32(/* id 6, wireType 2 =*/50).string(message.text);
                if (message.isFinal != null && Object.hasOwnProperty.call(message, "isFinal"))
                    writer.uint32(/* id 7, wireType 0 =*/56).bool(message.isFinal);
                return writer;
            };

            /**
             * Encodes the specified TtsTextChunk message, length delimited. Does not implicitly {@link fluent_audio.v1.TtsTextChunk.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.TtsTextChunk
             * @static
             * @param {fluent_audio.v1.ITtsTextChunk} message TtsTextChunk message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            TtsTextChunk.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes a TtsTextChunk message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.TtsTextChunk
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.TtsTextChunk} TtsTextChunk
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            TtsTextChunk.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.TtsTextChunk();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.requestId = reader.string();
                            break;
                        }
                    case 2: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 3: {
                            message.userTurnId = reader.string();
                            break;
                        }
                    case 4: {
                            message.assistantTurnId = reader.string();
                            break;
                        }
                    case 5: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 6: {
                            message.text = reader.string();
                            break;
                        }
                    case 7: {
                            message.isFinal = reader.bool();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes a TtsTextChunk message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.TtsTextChunk
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.TtsTextChunk} TtsTextChunk
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            TtsTextChunk.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a TtsTextChunk message.
             * @function verify
             * @memberof fluent_audio.v1.TtsTextChunk
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            TtsTextChunk.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    if (!$util.isString(message.requestId))
                        return "requestId: string expected";
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    if (!$util.isString(message.userTurnId))
                        return "userTurnId: string expected";
                if (message.assistantTurnId != null && Object.hasOwnProperty.call(message, "assistantTurnId"))
                    if (!$util.isString(message.assistantTurnId))
                        return "assistantTurnId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.text != null && Object.hasOwnProperty.call(message, "text"))
                    if (!$util.isString(message.text))
                        return "text: string expected";
                if (message.isFinal != null && Object.hasOwnProperty.call(message, "isFinal"))
                    if (typeof message.isFinal !== "boolean")
                        return "isFinal: boolean expected";
                return null;
            };

            /**
             * Creates a TtsTextChunk message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.TtsTextChunk
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.TtsTextChunk} TtsTextChunk
             */
            TtsTextChunk.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.TtsTextChunk)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.TtsTextChunk: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.TtsTextChunk();
                if (object.requestId != null)
                    message.requestId = String(object.requestId);
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.userTurnId != null)
                    message.userTurnId = String(object.userTurnId);
                if (object.assistantTurnId != null)
                    message.assistantTurnId = String(object.assistantTurnId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.text != null)
                    message.text = String(object.text);
                if (object.isFinal != null)
                    message.isFinal = Boolean(object.isFinal);
                return message;
            };

            /**
             * Creates a plain object from a TtsTextChunk message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.TtsTextChunk
             * @static
             * @param {fluent_audio.v1.TtsTextChunk} message TtsTextChunk
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            TtsTextChunk.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.requestId = "";
                    object.sessionId = "";
                    object.userTurnId = "";
                    object.assistantTurnId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    object.text = "";
                    object.isFinal = false;
                }
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    object.requestId = message.requestId;
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    object.userTurnId = message.userTurnId;
                if (message.assistantTurnId != null && Object.hasOwnProperty.call(message, "assistantTurnId"))
                    object.assistantTurnId = message.assistantTurnId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.text != null && Object.hasOwnProperty.call(message, "text"))
                    object.text = message.text;
                if (message.isFinal != null && Object.hasOwnProperty.call(message, "isFinal"))
                    object.isFinal = message.isFinal;
                return object;
            };

            /**
             * Converts this TtsTextChunk to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.TtsTextChunk
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            TtsTextChunk.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for TtsTextChunk
             * @function getTypeUrl
             * @memberof fluent_audio.v1.TtsTextChunk
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            TtsTextChunk.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.TtsTextChunk";
            };

            return TtsTextChunk;
        })();

        v1.TtsTextStreamFinal = (function() {

            /**
             * Properties of a TtsTextStreamFinal.
             * @memberof fluent_audio.v1
             * @interface ITtsTextStreamFinal
             * @property {string|null} [sessionId] TtsTextStreamFinal sessionId
             * @property {string|null} [userTurnId] TtsTextStreamFinal userTurnId
             * @property {string|null} [assistantTurnId] TtsTextStreamFinal assistantTurnId
             * @property {number|Long|null} [seq] TtsTextStreamFinal seq
             */

            /**
             * Constructs a new TtsTextStreamFinal.
             * @memberof fluent_audio.v1
             * @classdesc Represents a TtsTextStreamFinal.
             * @implements ITtsTextStreamFinal
             * @constructor
             * @param {fluent_audio.v1.ITtsTextStreamFinal=} [properties] Properties to set
             */
            function TtsTextStreamFinal(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * TtsTextStreamFinal sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.TtsTextStreamFinal
             * @instance
             */
            TtsTextStreamFinal.prototype.sessionId = "";

            /**
             * TtsTextStreamFinal userTurnId.
             * @member {string} userTurnId
             * @memberof fluent_audio.v1.TtsTextStreamFinal
             * @instance
             */
            TtsTextStreamFinal.prototype.userTurnId = "";

            /**
             * TtsTextStreamFinal assistantTurnId.
             * @member {string} assistantTurnId
             * @memberof fluent_audio.v1.TtsTextStreamFinal
             * @instance
             */
            TtsTextStreamFinal.prototype.assistantTurnId = "";

            /**
             * TtsTextStreamFinal seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.TtsTextStreamFinal
             * @instance
             */
            TtsTextStreamFinal.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * Creates a new TtsTextStreamFinal instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.TtsTextStreamFinal
             * @static
             * @param {fluent_audio.v1.ITtsTextStreamFinal=} [properties] Properties to set
             * @returns {fluent_audio.v1.TtsTextStreamFinal} TtsTextStreamFinal instance
             */
            TtsTextStreamFinal.create = function create(properties) {
                return new TtsTextStreamFinal(properties);
            };

            /**
             * Encodes the specified TtsTextStreamFinal message. Does not implicitly {@link fluent_audio.v1.TtsTextStreamFinal.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.TtsTextStreamFinal
             * @static
             * @param {fluent_audio.v1.ITtsTextStreamFinal} message TtsTextStreamFinal message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            TtsTextStreamFinal.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.sessionId);
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.userTurnId);
                if (message.assistantTurnId != null && Object.hasOwnProperty.call(message, "assistantTurnId"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.assistantTurnId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.seq);
                return writer;
            };

            /**
             * Encodes the specified TtsTextStreamFinal message, length delimited. Does not implicitly {@link fluent_audio.v1.TtsTextStreamFinal.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.TtsTextStreamFinal
             * @static
             * @param {fluent_audio.v1.ITtsTextStreamFinal} message TtsTextStreamFinal message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            TtsTextStreamFinal.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes a TtsTextStreamFinal message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.TtsTextStreamFinal
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.TtsTextStreamFinal} TtsTextStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            TtsTextStreamFinal.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.TtsTextStreamFinal();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 2: {
                            message.userTurnId = reader.string();
                            break;
                        }
                    case 3: {
                            message.assistantTurnId = reader.string();
                            break;
                        }
                    case 4: {
                            message.seq = reader.uint64();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes a TtsTextStreamFinal message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.TtsTextStreamFinal
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.TtsTextStreamFinal} TtsTextStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            TtsTextStreamFinal.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a TtsTextStreamFinal message.
             * @function verify
             * @memberof fluent_audio.v1.TtsTextStreamFinal
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            TtsTextStreamFinal.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    if (!$util.isString(message.userTurnId))
                        return "userTurnId: string expected";
                if (message.assistantTurnId != null && Object.hasOwnProperty.call(message, "assistantTurnId"))
                    if (!$util.isString(message.assistantTurnId))
                        return "assistantTurnId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                return null;
            };

            /**
             * Creates a TtsTextStreamFinal message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.TtsTextStreamFinal
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.TtsTextStreamFinal} TtsTextStreamFinal
             */
            TtsTextStreamFinal.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.TtsTextStreamFinal)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.TtsTextStreamFinal: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.TtsTextStreamFinal();
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.userTurnId != null)
                    message.userTurnId = String(object.userTurnId);
                if (object.assistantTurnId != null)
                    message.assistantTurnId = String(object.assistantTurnId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                return message;
            };

            /**
             * Creates a plain object from a TtsTextStreamFinal message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.TtsTextStreamFinal
             * @static
             * @param {fluent_audio.v1.TtsTextStreamFinal} message TtsTextStreamFinal
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            TtsTextStreamFinal.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.sessionId = "";
                    object.userTurnId = "";
                    object.assistantTurnId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                }
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    object.userTurnId = message.userTurnId;
                if (message.assistantTurnId != null && Object.hasOwnProperty.call(message, "assistantTurnId"))
                    object.assistantTurnId = message.assistantTurnId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                return object;
            };

            /**
             * Converts this TtsTextStreamFinal to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.TtsTextStreamFinal
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            TtsTextStreamFinal.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for TtsTextStreamFinal
             * @function getTypeUrl
             * @memberof fluent_audio.v1.TtsTextStreamFinal
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            TtsTextStreamFinal.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.TtsTextStreamFinal";
            };

            return TtsTextStreamFinal;
        })();

        v1.SynthesizedAudioChunk = (function() {

            /**
             * Properties of a SynthesizedAudioChunk.
             * @memberof fluent_audio.v1
             * @interface ISynthesizedAudioChunk
             * @property {string|null} [requestId] SynthesizedAudioChunk requestId
             * @property {string|null} [sessionId] SynthesizedAudioChunk sessionId
             * @property {string|null} [userTurnId] SynthesizedAudioChunk userTurnId
             * @property {string|null} [assistantTurnId] SynthesizedAudioChunk assistantTurnId
             * @property {number|Long|null} [seq] SynthesizedAudioChunk seq
             * @property {fluent_audio.v1.IAudioFrame|null} [audio] SynthesizedAudioChunk audio
             */

            /**
             * Constructs a new SynthesizedAudioChunk.
             * @memberof fluent_audio.v1
             * @classdesc Represents a SynthesizedAudioChunk.
             * @implements ISynthesizedAudioChunk
             * @constructor
             * @param {fluent_audio.v1.ISynthesizedAudioChunk=} [properties] Properties to set
             */
            function SynthesizedAudioChunk(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * SynthesizedAudioChunk requestId.
             * @member {string} requestId
             * @memberof fluent_audio.v1.SynthesizedAudioChunk
             * @instance
             */
            SynthesizedAudioChunk.prototype.requestId = "";

            /**
             * SynthesizedAudioChunk sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.SynthesizedAudioChunk
             * @instance
             */
            SynthesizedAudioChunk.prototype.sessionId = "";

            /**
             * SynthesizedAudioChunk userTurnId.
             * @member {string} userTurnId
             * @memberof fluent_audio.v1.SynthesizedAudioChunk
             * @instance
             */
            SynthesizedAudioChunk.prototype.userTurnId = "";

            /**
             * SynthesizedAudioChunk assistantTurnId.
             * @member {string} assistantTurnId
             * @memberof fluent_audio.v1.SynthesizedAudioChunk
             * @instance
             */
            SynthesizedAudioChunk.prototype.assistantTurnId = "";

            /**
             * SynthesizedAudioChunk seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.SynthesizedAudioChunk
             * @instance
             */
            SynthesizedAudioChunk.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * SynthesizedAudioChunk audio.
             * @member {fluent_audio.v1.IAudioFrame|null|undefined} audio
             * @memberof fluent_audio.v1.SynthesizedAudioChunk
             * @instance
             */
            SynthesizedAudioChunk.prototype.audio = null;

            /**
             * Creates a new SynthesizedAudioChunk instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.SynthesizedAudioChunk
             * @static
             * @param {fluent_audio.v1.ISynthesizedAudioChunk=} [properties] Properties to set
             * @returns {fluent_audio.v1.SynthesizedAudioChunk} SynthesizedAudioChunk instance
             */
            SynthesizedAudioChunk.create = function create(properties) {
                return new SynthesizedAudioChunk(properties);
            };

            /**
             * Encodes the specified SynthesizedAudioChunk message. Does not implicitly {@link fluent_audio.v1.SynthesizedAudioChunk.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.SynthesizedAudioChunk
             * @static
             * @param {fluent_audio.v1.ISynthesizedAudioChunk} message SynthesizedAudioChunk message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            SynthesizedAudioChunk.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.requestId);
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.sessionId);
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.userTurnId);
                if (message.assistantTurnId != null && Object.hasOwnProperty.call(message, "assistantTurnId"))
                    writer.uint32(/* id 4, wireType 2 =*/34).string(message.assistantTurnId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 5, wireType 0 =*/40).uint64(message.seq);
                if (message.audio != null && Object.hasOwnProperty.call(message, "audio"))
                    $root.fluent_audio.v1.AudioFrame.encode(message.audio, writer.uint32(/* id 6, wireType 2 =*/50).fork(), q + 1).ldelim();
                return writer;
            };

            /**
             * Encodes the specified SynthesizedAudioChunk message, length delimited. Does not implicitly {@link fluent_audio.v1.SynthesizedAudioChunk.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.SynthesizedAudioChunk
             * @static
             * @param {fluent_audio.v1.ISynthesizedAudioChunk} message SynthesizedAudioChunk message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            SynthesizedAudioChunk.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes a SynthesizedAudioChunk message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.SynthesizedAudioChunk
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.SynthesizedAudioChunk} SynthesizedAudioChunk
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            SynthesizedAudioChunk.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.SynthesizedAudioChunk();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.requestId = reader.string();
                            break;
                        }
                    case 2: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 3: {
                            message.userTurnId = reader.string();
                            break;
                        }
                    case 4: {
                            message.assistantTurnId = reader.string();
                            break;
                        }
                    case 5: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 6: {
                            message.audio = $root.fluent_audio.v1.AudioFrame.decode(reader, reader.uint32(), undefined, long + 1);
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes a SynthesizedAudioChunk message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.SynthesizedAudioChunk
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.SynthesizedAudioChunk} SynthesizedAudioChunk
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            SynthesizedAudioChunk.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a SynthesizedAudioChunk message.
             * @function verify
             * @memberof fluent_audio.v1.SynthesizedAudioChunk
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            SynthesizedAudioChunk.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    if (!$util.isString(message.requestId))
                        return "requestId: string expected";
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    if (!$util.isString(message.userTurnId))
                        return "userTurnId: string expected";
                if (message.assistantTurnId != null && Object.hasOwnProperty.call(message, "assistantTurnId"))
                    if (!$util.isString(message.assistantTurnId))
                        return "assistantTurnId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.audio != null && Object.hasOwnProperty.call(message, "audio")) {
                    var error = $root.fluent_audio.v1.AudioFrame.verify(message.audio, long + 1);
                    if (error)
                        return "audio." + error;
                }
                return null;
            };

            /**
             * Creates a SynthesizedAudioChunk message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.SynthesizedAudioChunk
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.SynthesizedAudioChunk} SynthesizedAudioChunk
             */
            SynthesizedAudioChunk.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.SynthesizedAudioChunk)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.SynthesizedAudioChunk: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.SynthesizedAudioChunk();
                if (object.requestId != null)
                    message.requestId = String(object.requestId);
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.userTurnId != null)
                    message.userTurnId = String(object.userTurnId);
                if (object.assistantTurnId != null)
                    message.assistantTurnId = String(object.assistantTurnId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.audio != null) {
                    if (!$util.isObject(object.audio))
                        throw TypeError(".fluent_audio.v1.SynthesizedAudioChunk.audio: object expected");
                    message.audio = $root.fluent_audio.v1.AudioFrame.fromObject(object.audio, long + 1);
                }
                return message;
            };

            /**
             * Creates a plain object from a SynthesizedAudioChunk message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.SynthesizedAudioChunk
             * @static
             * @param {fluent_audio.v1.SynthesizedAudioChunk} message SynthesizedAudioChunk
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            SynthesizedAudioChunk.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.requestId = "";
                    object.sessionId = "";
                    object.userTurnId = "";
                    object.assistantTurnId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    object.audio = null;
                }
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    object.requestId = message.requestId;
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    object.userTurnId = message.userTurnId;
                if (message.assistantTurnId != null && Object.hasOwnProperty.call(message, "assistantTurnId"))
                    object.assistantTurnId = message.assistantTurnId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.audio != null && Object.hasOwnProperty.call(message, "audio"))
                    object.audio = $root.fluent_audio.v1.AudioFrame.toObject(message.audio, options, q + 1);
                return object;
            };

            /**
             * Converts this SynthesizedAudioChunk to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.SynthesizedAudioChunk
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            SynthesizedAudioChunk.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for SynthesizedAudioChunk
             * @function getTypeUrl
             * @memberof fluent_audio.v1.SynthesizedAudioChunk
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            SynthesizedAudioChunk.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.SynthesizedAudioChunk";
            };

            return SynthesizedAudioChunk;
        })();

        v1.SynthesizedAudioStreamFinal = (function() {

            /**
             * Properties of a SynthesizedAudioStreamFinal.
             * @memberof fluent_audio.v1
             * @interface ISynthesizedAudioStreamFinal
             * @property {string|null} [requestId] SynthesizedAudioStreamFinal requestId
             * @property {string|null} [sessionId] SynthesizedAudioStreamFinal sessionId
             * @property {string|null} [userTurnId] SynthesizedAudioStreamFinal userTurnId
             * @property {string|null} [assistantTurnId] SynthesizedAudioStreamFinal assistantTurnId
             * @property {number|Long|null} [seq] SynthesizedAudioStreamFinal seq
             * @property {string|null} [audioSourceId] SynthesizedAudioStreamFinal audioSourceId
             * @property {string|null} [audioStreamId] SynthesizedAudioStreamFinal audioStreamId
             * @property {number|Long|null} [audioSeq] SynthesizedAudioStreamFinal audioSeq
             * @property {number|Long|null} [audioSampleIndex] SynthesizedAudioStreamFinal audioSampleIndex
             * @property {number|Long|null} [audioCaptureTimeNs] SynthesizedAudioStreamFinal audioCaptureTimeNs
             * @property {fluent_audio.v1.IAudioFormat|null} [audioFormat] SynthesizedAudioStreamFinal audioFormat
             */

            /**
             * Constructs a new SynthesizedAudioStreamFinal.
             * @memberof fluent_audio.v1
             * @classdesc Represents a SynthesizedAudioStreamFinal.
             * @implements ISynthesizedAudioStreamFinal
             * @constructor
             * @param {fluent_audio.v1.ISynthesizedAudioStreamFinal=} [properties] Properties to set
             */
            function SynthesizedAudioStreamFinal(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * SynthesizedAudioStreamFinal requestId.
             * @member {string} requestId
             * @memberof fluent_audio.v1.SynthesizedAudioStreamFinal
             * @instance
             */
            SynthesizedAudioStreamFinal.prototype.requestId = "";

            /**
             * SynthesizedAudioStreamFinal sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.SynthesizedAudioStreamFinal
             * @instance
             */
            SynthesizedAudioStreamFinal.prototype.sessionId = "";

            /**
             * SynthesizedAudioStreamFinal userTurnId.
             * @member {string} userTurnId
             * @memberof fluent_audio.v1.SynthesizedAudioStreamFinal
             * @instance
             */
            SynthesizedAudioStreamFinal.prototype.userTurnId = "";

            /**
             * SynthesizedAudioStreamFinal assistantTurnId.
             * @member {string} assistantTurnId
             * @memberof fluent_audio.v1.SynthesizedAudioStreamFinal
             * @instance
             */
            SynthesizedAudioStreamFinal.prototype.assistantTurnId = "";

            /**
             * SynthesizedAudioStreamFinal seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.SynthesizedAudioStreamFinal
             * @instance
             */
            SynthesizedAudioStreamFinal.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * SynthesizedAudioStreamFinal audioSourceId.
             * @member {string} audioSourceId
             * @memberof fluent_audio.v1.SynthesizedAudioStreamFinal
             * @instance
             */
            SynthesizedAudioStreamFinal.prototype.audioSourceId = "";

            /**
             * SynthesizedAudioStreamFinal audioStreamId.
             * @member {string} audioStreamId
             * @memberof fluent_audio.v1.SynthesizedAudioStreamFinal
             * @instance
             */
            SynthesizedAudioStreamFinal.prototype.audioStreamId = "";

            /**
             * SynthesizedAudioStreamFinal audioSeq.
             * @member {number|Long} audioSeq
             * @memberof fluent_audio.v1.SynthesizedAudioStreamFinal
             * @instance
             */
            SynthesizedAudioStreamFinal.prototype.audioSeq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * SynthesizedAudioStreamFinal audioSampleIndex.
             * @member {number|Long} audioSampleIndex
             * @memberof fluent_audio.v1.SynthesizedAudioStreamFinal
             * @instance
             */
            SynthesizedAudioStreamFinal.prototype.audioSampleIndex = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * SynthesizedAudioStreamFinal audioCaptureTimeNs.
             * @member {number|Long} audioCaptureTimeNs
             * @memberof fluent_audio.v1.SynthesizedAudioStreamFinal
             * @instance
             */
            SynthesizedAudioStreamFinal.prototype.audioCaptureTimeNs = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * SynthesizedAudioStreamFinal audioFormat.
             * @member {fluent_audio.v1.IAudioFormat|null|undefined} audioFormat
             * @memberof fluent_audio.v1.SynthesizedAudioStreamFinal
             * @instance
             */
            SynthesizedAudioStreamFinal.prototype.audioFormat = null;

            /**
             * Creates a new SynthesizedAudioStreamFinal instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.SynthesizedAudioStreamFinal
             * @static
             * @param {fluent_audio.v1.ISynthesizedAudioStreamFinal=} [properties] Properties to set
             * @returns {fluent_audio.v1.SynthesizedAudioStreamFinal} SynthesizedAudioStreamFinal instance
             */
            SynthesizedAudioStreamFinal.create = function create(properties) {
                return new SynthesizedAudioStreamFinal(properties);
            };

            /**
             * Encodes the specified SynthesizedAudioStreamFinal message. Does not implicitly {@link fluent_audio.v1.SynthesizedAudioStreamFinal.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.SynthesizedAudioStreamFinal
             * @static
             * @param {fluent_audio.v1.ISynthesizedAudioStreamFinal} message SynthesizedAudioStreamFinal message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            SynthesizedAudioStreamFinal.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.requestId);
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.sessionId);
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.userTurnId);
                if (message.assistantTurnId != null && Object.hasOwnProperty.call(message, "assistantTurnId"))
                    writer.uint32(/* id 4, wireType 2 =*/34).string(message.assistantTurnId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 5, wireType 0 =*/40).uint64(message.seq);
                if (message.audioSourceId != null && Object.hasOwnProperty.call(message, "audioSourceId"))
                    writer.uint32(/* id 6, wireType 2 =*/50).string(message.audioSourceId);
                if (message.audioStreamId != null && Object.hasOwnProperty.call(message, "audioStreamId"))
                    writer.uint32(/* id 7, wireType 2 =*/58).string(message.audioStreamId);
                if (message.audioSeq != null && Object.hasOwnProperty.call(message, "audioSeq"))
                    writer.uint32(/* id 8, wireType 0 =*/64).uint64(message.audioSeq);
                if (message.audioSampleIndex != null && Object.hasOwnProperty.call(message, "audioSampleIndex"))
                    writer.uint32(/* id 9, wireType 0 =*/72).uint64(message.audioSampleIndex);
                if (message.audioCaptureTimeNs != null && Object.hasOwnProperty.call(message, "audioCaptureTimeNs"))
                    writer.uint32(/* id 10, wireType 0 =*/80).uint64(message.audioCaptureTimeNs);
                if (message.audioFormat != null && Object.hasOwnProperty.call(message, "audioFormat"))
                    $root.fluent_audio.v1.AudioFormat.encode(message.audioFormat, writer.uint32(/* id 11, wireType 2 =*/90).fork(), q + 1).ldelim();
                return writer;
            };

            /**
             * Encodes the specified SynthesizedAudioStreamFinal message, length delimited. Does not implicitly {@link fluent_audio.v1.SynthesizedAudioStreamFinal.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.SynthesizedAudioStreamFinal
             * @static
             * @param {fluent_audio.v1.ISynthesizedAudioStreamFinal} message SynthesizedAudioStreamFinal message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            SynthesizedAudioStreamFinal.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes a SynthesizedAudioStreamFinal message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.SynthesizedAudioStreamFinal
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.SynthesizedAudioStreamFinal} SynthesizedAudioStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            SynthesizedAudioStreamFinal.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.SynthesizedAudioStreamFinal();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.requestId = reader.string();
                            break;
                        }
                    case 2: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 3: {
                            message.userTurnId = reader.string();
                            break;
                        }
                    case 4: {
                            message.assistantTurnId = reader.string();
                            break;
                        }
                    case 5: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 6: {
                            message.audioSourceId = reader.string();
                            break;
                        }
                    case 7: {
                            message.audioStreamId = reader.string();
                            break;
                        }
                    case 8: {
                            message.audioSeq = reader.uint64();
                            break;
                        }
                    case 9: {
                            message.audioSampleIndex = reader.uint64();
                            break;
                        }
                    case 10: {
                            message.audioCaptureTimeNs = reader.uint64();
                            break;
                        }
                    case 11: {
                            message.audioFormat = $root.fluent_audio.v1.AudioFormat.decode(reader, reader.uint32(), undefined, long + 1);
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes a SynthesizedAudioStreamFinal message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.SynthesizedAudioStreamFinal
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.SynthesizedAudioStreamFinal} SynthesizedAudioStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            SynthesizedAudioStreamFinal.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a SynthesizedAudioStreamFinal message.
             * @function verify
             * @memberof fluent_audio.v1.SynthesizedAudioStreamFinal
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            SynthesizedAudioStreamFinal.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    if (!$util.isString(message.requestId))
                        return "requestId: string expected";
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    if (!$util.isString(message.userTurnId))
                        return "userTurnId: string expected";
                if (message.assistantTurnId != null && Object.hasOwnProperty.call(message, "assistantTurnId"))
                    if (!$util.isString(message.assistantTurnId))
                        return "assistantTurnId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.audioSourceId != null && Object.hasOwnProperty.call(message, "audioSourceId"))
                    if (!$util.isString(message.audioSourceId))
                        return "audioSourceId: string expected";
                if (message.audioStreamId != null && Object.hasOwnProperty.call(message, "audioStreamId"))
                    if (!$util.isString(message.audioStreamId))
                        return "audioStreamId: string expected";
                if (message.audioSeq != null && Object.hasOwnProperty.call(message, "audioSeq"))
                    if (!$util.isInteger(message.audioSeq) && !(message.audioSeq && $util.isInteger(message.audioSeq.low) && $util.isInteger(message.audioSeq.high)))
                        return "audioSeq: integer|Long expected";
                if (message.audioSampleIndex != null && Object.hasOwnProperty.call(message, "audioSampleIndex"))
                    if (!$util.isInteger(message.audioSampleIndex) && !(message.audioSampleIndex && $util.isInteger(message.audioSampleIndex.low) && $util.isInteger(message.audioSampleIndex.high)))
                        return "audioSampleIndex: integer|Long expected";
                if (message.audioCaptureTimeNs != null && Object.hasOwnProperty.call(message, "audioCaptureTimeNs"))
                    if (!$util.isInteger(message.audioCaptureTimeNs) && !(message.audioCaptureTimeNs && $util.isInteger(message.audioCaptureTimeNs.low) && $util.isInteger(message.audioCaptureTimeNs.high)))
                        return "audioCaptureTimeNs: integer|Long expected";
                if (message.audioFormat != null && Object.hasOwnProperty.call(message, "audioFormat")) {
                    var error = $root.fluent_audio.v1.AudioFormat.verify(message.audioFormat, long + 1);
                    if (error)
                        return "audioFormat." + error;
                }
                return null;
            };

            /**
             * Creates a SynthesizedAudioStreamFinal message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.SynthesizedAudioStreamFinal
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.SynthesizedAudioStreamFinal} SynthesizedAudioStreamFinal
             */
            SynthesizedAudioStreamFinal.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.SynthesizedAudioStreamFinal)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.SynthesizedAudioStreamFinal: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.SynthesizedAudioStreamFinal();
                if (object.requestId != null)
                    message.requestId = String(object.requestId);
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.userTurnId != null)
                    message.userTurnId = String(object.userTurnId);
                if (object.assistantTurnId != null)
                    message.assistantTurnId = String(object.assistantTurnId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.audioSourceId != null)
                    message.audioSourceId = String(object.audioSourceId);
                if (object.audioStreamId != null)
                    message.audioStreamId = String(object.audioStreamId);
                if (object.audioSeq != null)
                    if ($util.Long)
                        message.audioSeq = $util.Long.fromValue(object.audioSeq, true);
                    else if (typeof object.audioSeq === "string")
                        message.audioSeq = parseInt(object.audioSeq, 10);
                    else if (typeof object.audioSeq === "number")
                        message.audioSeq = object.audioSeq;
                    else if (typeof object.audioSeq === "object")
                        message.audioSeq = new $util.LongBits(object.audioSeq.low >>> 0, object.audioSeq.high >>> 0).toNumber(true);
                if (object.audioSampleIndex != null)
                    if ($util.Long)
                        message.audioSampleIndex = $util.Long.fromValue(object.audioSampleIndex, true);
                    else if (typeof object.audioSampleIndex === "string")
                        message.audioSampleIndex = parseInt(object.audioSampleIndex, 10);
                    else if (typeof object.audioSampleIndex === "number")
                        message.audioSampleIndex = object.audioSampleIndex;
                    else if (typeof object.audioSampleIndex === "object")
                        message.audioSampleIndex = new $util.LongBits(object.audioSampleIndex.low >>> 0, object.audioSampleIndex.high >>> 0).toNumber(true);
                if (object.audioCaptureTimeNs != null)
                    if ($util.Long)
                        message.audioCaptureTimeNs = $util.Long.fromValue(object.audioCaptureTimeNs, true);
                    else if (typeof object.audioCaptureTimeNs === "string")
                        message.audioCaptureTimeNs = parseInt(object.audioCaptureTimeNs, 10);
                    else if (typeof object.audioCaptureTimeNs === "number")
                        message.audioCaptureTimeNs = object.audioCaptureTimeNs;
                    else if (typeof object.audioCaptureTimeNs === "object")
                        message.audioCaptureTimeNs = new $util.LongBits(object.audioCaptureTimeNs.low >>> 0, object.audioCaptureTimeNs.high >>> 0).toNumber(true);
                if (object.audioFormat != null) {
                    if (!$util.isObject(object.audioFormat))
                        throw TypeError(".fluent_audio.v1.SynthesizedAudioStreamFinal.audioFormat: object expected");
                    message.audioFormat = $root.fluent_audio.v1.AudioFormat.fromObject(object.audioFormat, long + 1);
                }
                return message;
            };

            /**
             * Creates a plain object from a SynthesizedAudioStreamFinal message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.SynthesizedAudioStreamFinal
             * @static
             * @param {fluent_audio.v1.SynthesizedAudioStreamFinal} message SynthesizedAudioStreamFinal
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            SynthesizedAudioStreamFinal.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.requestId = "";
                    object.sessionId = "";
                    object.userTurnId = "";
                    object.assistantTurnId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    object.audioSourceId = "";
                    object.audioStreamId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.audioSeq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.audioSeq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.audioSampleIndex = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.audioSampleIndex = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.audioCaptureTimeNs = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.audioCaptureTimeNs = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    object.audioFormat = null;
                }
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    object.requestId = message.requestId;
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    object.userTurnId = message.userTurnId;
                if (message.assistantTurnId != null && Object.hasOwnProperty.call(message, "assistantTurnId"))
                    object.assistantTurnId = message.assistantTurnId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.audioSourceId != null && Object.hasOwnProperty.call(message, "audioSourceId"))
                    object.audioSourceId = message.audioSourceId;
                if (message.audioStreamId != null && Object.hasOwnProperty.call(message, "audioStreamId"))
                    object.audioStreamId = message.audioStreamId;
                if (message.audioSeq != null && Object.hasOwnProperty.call(message, "audioSeq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.audioSeq = typeof message.audioSeq === "number" ? BigInt(message.audioSeq) : $util.Long.fromBits(message.audioSeq.low >>> 0, message.audioSeq.high >>> 0, true).toBigInt();
                    else if (typeof message.audioSeq === "number")
                        object.audioSeq = options.longs === String ? String(message.audioSeq) : message.audioSeq;
                    else
                        object.audioSeq = options.longs === String ? $util.Long.prototype.toString.call(message.audioSeq) : options.longs === Number ? new $util.LongBits(message.audioSeq.low >>> 0, message.audioSeq.high >>> 0).toNumber(true) : message.audioSeq;
                if (message.audioSampleIndex != null && Object.hasOwnProperty.call(message, "audioSampleIndex"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.audioSampleIndex = typeof message.audioSampleIndex === "number" ? BigInt(message.audioSampleIndex) : $util.Long.fromBits(message.audioSampleIndex.low >>> 0, message.audioSampleIndex.high >>> 0, true).toBigInt();
                    else if (typeof message.audioSampleIndex === "number")
                        object.audioSampleIndex = options.longs === String ? String(message.audioSampleIndex) : message.audioSampleIndex;
                    else
                        object.audioSampleIndex = options.longs === String ? $util.Long.prototype.toString.call(message.audioSampleIndex) : options.longs === Number ? new $util.LongBits(message.audioSampleIndex.low >>> 0, message.audioSampleIndex.high >>> 0).toNumber(true) : message.audioSampleIndex;
                if (message.audioCaptureTimeNs != null && Object.hasOwnProperty.call(message, "audioCaptureTimeNs"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.audioCaptureTimeNs = typeof message.audioCaptureTimeNs === "number" ? BigInt(message.audioCaptureTimeNs) : $util.Long.fromBits(message.audioCaptureTimeNs.low >>> 0, message.audioCaptureTimeNs.high >>> 0, true).toBigInt();
                    else if (typeof message.audioCaptureTimeNs === "number")
                        object.audioCaptureTimeNs = options.longs === String ? String(message.audioCaptureTimeNs) : message.audioCaptureTimeNs;
                    else
                        object.audioCaptureTimeNs = options.longs === String ? $util.Long.prototype.toString.call(message.audioCaptureTimeNs) : options.longs === Number ? new $util.LongBits(message.audioCaptureTimeNs.low >>> 0, message.audioCaptureTimeNs.high >>> 0).toNumber(true) : message.audioCaptureTimeNs;
                if (message.audioFormat != null && Object.hasOwnProperty.call(message, "audioFormat"))
                    object.audioFormat = $root.fluent_audio.v1.AudioFormat.toObject(message.audioFormat, options, q + 1);
                return object;
            };

            /**
             * Converts this SynthesizedAudioStreamFinal to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.SynthesizedAudioStreamFinal
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            SynthesizedAudioStreamFinal.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for SynthesizedAudioStreamFinal
             * @function getTypeUrl
             * @memberof fluent_audio.v1.SynthesizedAudioStreamFinal
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            SynthesizedAudioStreamFinal.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.SynthesizedAudioStreamFinal";
            };

            return SynthesizedAudioStreamFinal;
        })();

        /**
         * VoiceSessionState enum.
         * @name fluent_audio.v1.VoiceSessionState
         * @enum {number}
         * @property {number} VOICE_SESSION_STATE_UNSPECIFIED=0 VOICE_SESSION_STATE_UNSPECIFIED value
         * @property {number} VOICE_SESSION_STATE_IDLE=1 VOICE_SESSION_STATE_IDLE value
         * @property {number} VOICE_SESSION_STATE_LISTENING=2 VOICE_SESSION_STATE_LISTENING value
         * @property {number} VOICE_SESSION_STATE_USER_SPEAKING=3 VOICE_SESSION_STATE_USER_SPEAKING value
         * @property {number} VOICE_SESSION_STATE_TRANSCRIBING=4 VOICE_SESSION_STATE_TRANSCRIBING value
         * @property {number} VOICE_SESSION_STATE_THINKING=5 VOICE_SESSION_STATE_THINKING value
         * @property {number} VOICE_SESSION_STATE_SPEAKING=6 VOICE_SESSION_STATE_SPEAKING value
         * @property {number} VOICE_SESSION_STATE_INTERRUPTED=7 VOICE_SESSION_STATE_INTERRUPTED value
         * @property {number} VOICE_SESSION_STATE_CLOSED=8 VOICE_SESSION_STATE_CLOSED value
         * @property {number} VOICE_SESSION_STATE_ERROR=9 VOICE_SESSION_STATE_ERROR value
         */
        v1.VoiceSessionState = (function() {
            var valuesById = {}, values = Object.create(valuesById);
            values[valuesById[0] = "VOICE_SESSION_STATE_UNSPECIFIED"] = 0;
            values[valuesById[1] = "VOICE_SESSION_STATE_IDLE"] = 1;
            values[valuesById[2] = "VOICE_SESSION_STATE_LISTENING"] = 2;
            values[valuesById[3] = "VOICE_SESSION_STATE_USER_SPEAKING"] = 3;
            values[valuesById[4] = "VOICE_SESSION_STATE_TRANSCRIBING"] = 4;
            values[valuesById[5] = "VOICE_SESSION_STATE_THINKING"] = 5;
            values[valuesById[6] = "VOICE_SESSION_STATE_SPEAKING"] = 6;
            values[valuesById[7] = "VOICE_SESSION_STATE_INTERRUPTED"] = 7;
            values[valuesById[8] = "VOICE_SESSION_STATE_CLOSED"] = 8;
            values[valuesById[9] = "VOICE_SESSION_STATE_ERROR"] = 9;
            return values;
        })();

        /**
         * VoiceSessionEventKind enum.
         * @name fluent_audio.v1.VoiceSessionEventKind
         * @enum {number}
         * @property {number} VOICE_SESSION_EVENT_KIND_UNSPECIFIED=0 VOICE_SESSION_EVENT_KIND_UNSPECIFIED value
         * @property {number} VOICE_SESSION_EVENT_KIND_SESSION_STARTED=1 VOICE_SESSION_EVENT_KIND_SESSION_STARTED value
         * @property {number} VOICE_SESSION_EVENT_KIND_STATE_CHANGED=2 VOICE_SESSION_EVENT_KIND_STATE_CHANGED value
         * @property {number} VOICE_SESSION_EVENT_KIND_USER_TURN_STARTED=3 VOICE_SESSION_EVENT_KIND_USER_TURN_STARTED value
         * @property {number} VOICE_SESSION_EVENT_KIND_USER_TURN_FINALIZED=4 VOICE_SESSION_EVENT_KIND_USER_TURN_FINALIZED value
         * @property {number} VOICE_SESSION_EVENT_KIND_ASSISTANT_TURN_STARTED=5 VOICE_SESSION_EVENT_KIND_ASSISTANT_TURN_STARTED value
         * @property {number} VOICE_SESSION_EVENT_KIND_ASSISTANT_TURN_COMPLETED=6 VOICE_SESSION_EVENT_KIND_ASSISTANT_TURN_COMPLETED value
         * @property {number} VOICE_SESSION_EVENT_KIND_SESSION_CLOSED=7 VOICE_SESSION_EVENT_KIND_SESSION_CLOSED value
         * @property {number} VOICE_SESSION_EVENT_KIND_ERROR=8 VOICE_SESSION_EVENT_KIND_ERROR value
         */
        v1.VoiceSessionEventKind = (function() {
            var valuesById = {}, values = Object.create(valuesById);
            values[valuesById[0] = "VOICE_SESSION_EVENT_KIND_UNSPECIFIED"] = 0;
            values[valuesById[1] = "VOICE_SESSION_EVENT_KIND_SESSION_STARTED"] = 1;
            values[valuesById[2] = "VOICE_SESSION_EVENT_KIND_STATE_CHANGED"] = 2;
            values[valuesById[3] = "VOICE_SESSION_EVENT_KIND_USER_TURN_STARTED"] = 3;
            values[valuesById[4] = "VOICE_SESSION_EVENT_KIND_USER_TURN_FINALIZED"] = 4;
            values[valuesById[5] = "VOICE_SESSION_EVENT_KIND_ASSISTANT_TURN_STARTED"] = 5;
            values[valuesById[6] = "VOICE_SESSION_EVENT_KIND_ASSISTANT_TURN_COMPLETED"] = 6;
            values[valuesById[7] = "VOICE_SESSION_EVENT_KIND_SESSION_CLOSED"] = 7;
            values[valuesById[8] = "VOICE_SESSION_EVENT_KIND_ERROR"] = 8;
            return values;
        })();

        v1.TurnIds = (function() {

            /**
             * Properties of a TurnIds.
             * @memberof fluent_audio.v1
             * @interface ITurnIds
             * @property {string|null} [sessionId] TurnIds sessionId
             * @property {string|null} [userTurnId] TurnIds userTurnId
             * @property {string|null} [assistantTurnId] TurnIds assistantTurnId
             */

            /**
             * Constructs a new TurnIds.
             * @memberof fluent_audio.v1
             * @classdesc Represents a TurnIds.
             * @implements ITurnIds
             * @constructor
             * @param {fluent_audio.v1.ITurnIds=} [properties] Properties to set
             */
            function TurnIds(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * TurnIds sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.TurnIds
             * @instance
             */
            TurnIds.prototype.sessionId = "";

            /**
             * TurnIds userTurnId.
             * @member {string} userTurnId
             * @memberof fluent_audio.v1.TurnIds
             * @instance
             */
            TurnIds.prototype.userTurnId = "";

            /**
             * TurnIds assistantTurnId.
             * @member {string|null|undefined} assistantTurnId
             * @memberof fluent_audio.v1.TurnIds
             * @instance
             */
            TurnIds.prototype.assistantTurnId = null;

            // OneOf field names bound to virtual getters and setters
            var $oneOfFields;

            // Virtual OneOf for proto3 optional field
            Object.defineProperty(TurnIds.prototype, "_assistantTurnId", {
                get: $util.oneOfGetter($oneOfFields = ["assistantTurnId"]),
                set: $util.oneOfSetter($oneOfFields)
            });

            /**
             * Creates a new TurnIds instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.TurnIds
             * @static
             * @param {fluent_audio.v1.ITurnIds=} [properties] Properties to set
             * @returns {fluent_audio.v1.TurnIds} TurnIds instance
             */
            TurnIds.create = function create(properties) {
                return new TurnIds(properties);
            };

            /**
             * Encodes the specified TurnIds message. Does not implicitly {@link fluent_audio.v1.TurnIds.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.TurnIds
             * @static
             * @param {fluent_audio.v1.ITurnIds} message TurnIds message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            TurnIds.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.sessionId);
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.userTurnId);
                if (message.assistantTurnId != null && Object.hasOwnProperty.call(message, "assistantTurnId"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.assistantTurnId);
                return writer;
            };

            /**
             * Encodes the specified TurnIds message, length delimited. Does not implicitly {@link fluent_audio.v1.TurnIds.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.TurnIds
             * @static
             * @param {fluent_audio.v1.ITurnIds} message TurnIds message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            TurnIds.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes a TurnIds message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.TurnIds
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.TurnIds} TurnIds
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            TurnIds.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.TurnIds();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 2: {
                            message.userTurnId = reader.string();
                            break;
                        }
                    case 3: {
                            message.assistantTurnId = reader.string();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes a TurnIds message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.TurnIds
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.TurnIds} TurnIds
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            TurnIds.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a TurnIds message.
             * @function verify
             * @memberof fluent_audio.v1.TurnIds
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            TurnIds.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                var properties = {};
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    if (!$util.isString(message.userTurnId))
                        return "userTurnId: string expected";
                if (message.assistantTurnId != null && Object.hasOwnProperty.call(message, "assistantTurnId")) {
                    properties._assistantTurnId = 1;
                    if (!$util.isString(message.assistantTurnId))
                        return "assistantTurnId: string expected";
                }
                return null;
            };

            /**
             * Creates a TurnIds message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.TurnIds
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.TurnIds} TurnIds
             */
            TurnIds.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.TurnIds)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.TurnIds: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.TurnIds();
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.userTurnId != null)
                    message.userTurnId = String(object.userTurnId);
                if (object.assistantTurnId != null)
                    message.assistantTurnId = String(object.assistantTurnId);
                return message;
            };

            /**
             * Creates a plain object from a TurnIds message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.TurnIds
             * @static
             * @param {fluent_audio.v1.TurnIds} message TurnIds
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            TurnIds.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.sessionId = "";
                    object.userTurnId = "";
                }
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    object.userTurnId = message.userTurnId;
                if (message.assistantTurnId != null && Object.hasOwnProperty.call(message, "assistantTurnId")) {
                    object.assistantTurnId = message.assistantTurnId;
                    if (options.oneofs)
                        object._assistantTurnId = "assistantTurnId";
                }
                return object;
            };

            /**
             * Converts this TurnIds to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.TurnIds
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            TurnIds.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for TurnIds
             * @function getTypeUrl
             * @memberof fluent_audio.v1.TurnIds
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            TurnIds.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.TurnIds";
            };

            return TurnIds;
        })();

        v1.VoiceSessionEvent = (function() {

            /**
             * Properties of a VoiceSessionEvent.
             * @memberof fluent_audio.v1
             * @interface IVoiceSessionEvent
             * @property {fluent_audio.v1.VoiceSessionEventKind|null} [event] VoiceSessionEvent event
             * @property {fluent_audio.v1.VoiceSessionState|null} [state] VoiceSessionEvent state
             * @property {number|Long|null} [seq] VoiceSessionEvent seq
             * @property {fluent_audio.v1.ITurnIds|null} [turnIds] VoiceSessionEvent turnIds
             * @property {string|null} [message] VoiceSessionEvent message
             */

            /**
             * Constructs a new VoiceSessionEvent.
             * @memberof fluent_audio.v1
             * @classdesc Represents a VoiceSessionEvent.
             * @implements IVoiceSessionEvent
             * @constructor
             * @param {fluent_audio.v1.IVoiceSessionEvent=} [properties] Properties to set
             */
            function VoiceSessionEvent(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * VoiceSessionEvent event.
             * @member {fluent_audio.v1.VoiceSessionEventKind} event
             * @memberof fluent_audio.v1.VoiceSessionEvent
             * @instance
             */
            VoiceSessionEvent.prototype.event = 0;

            /**
             * VoiceSessionEvent state.
             * @member {fluent_audio.v1.VoiceSessionState} state
             * @memberof fluent_audio.v1.VoiceSessionEvent
             * @instance
             */
            VoiceSessionEvent.prototype.state = 0;

            /**
             * VoiceSessionEvent seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.VoiceSessionEvent
             * @instance
             */
            VoiceSessionEvent.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * VoiceSessionEvent turnIds.
             * @member {fluent_audio.v1.ITurnIds|null|undefined} turnIds
             * @memberof fluent_audio.v1.VoiceSessionEvent
             * @instance
             */
            VoiceSessionEvent.prototype.turnIds = null;

            /**
             * VoiceSessionEvent message.
             * @member {string|null|undefined} message
             * @memberof fluent_audio.v1.VoiceSessionEvent
             * @instance
             */
            VoiceSessionEvent.prototype.message = null;

            // OneOf field names bound to virtual getters and setters
            var $oneOfFields;

            // Virtual OneOf for proto3 optional field
            Object.defineProperty(VoiceSessionEvent.prototype, "_message", {
                get: $util.oneOfGetter($oneOfFields = ["message"]),
                set: $util.oneOfSetter($oneOfFields)
            });

            /**
             * Creates a new VoiceSessionEvent instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.VoiceSessionEvent
             * @static
             * @param {fluent_audio.v1.IVoiceSessionEvent=} [properties] Properties to set
             * @returns {fluent_audio.v1.VoiceSessionEvent} VoiceSessionEvent instance
             */
            VoiceSessionEvent.create = function create(properties) {
                return new VoiceSessionEvent(properties);
            };

            /**
             * Encodes the specified VoiceSessionEvent message. Does not implicitly {@link fluent_audio.v1.VoiceSessionEvent.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.VoiceSessionEvent
             * @static
             * @param {fluent_audio.v1.IVoiceSessionEvent} message VoiceSessionEvent message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            VoiceSessionEvent.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.event != null && Object.hasOwnProperty.call(message, "event"))
                    writer.uint32(/* id 1, wireType 0 =*/8).int32(message.event);
                if (message.state != null && Object.hasOwnProperty.call(message, "state"))
                    writer.uint32(/* id 2, wireType 0 =*/16).int32(message.state);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 3, wireType 0 =*/24).uint64(message.seq);
                if (message.turnIds != null && Object.hasOwnProperty.call(message, "turnIds"))
                    $root.fluent_audio.v1.TurnIds.encode(message.turnIds, writer.uint32(/* id 4, wireType 2 =*/34).fork(), q + 1).ldelim();
                if (message.message != null && Object.hasOwnProperty.call(message, "message"))
                    writer.uint32(/* id 5, wireType 2 =*/42).string(message.message);
                return writer;
            };

            /**
             * Encodes the specified VoiceSessionEvent message, length delimited. Does not implicitly {@link fluent_audio.v1.VoiceSessionEvent.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.VoiceSessionEvent
             * @static
             * @param {fluent_audio.v1.IVoiceSessionEvent} message VoiceSessionEvent message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            VoiceSessionEvent.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes a VoiceSessionEvent message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.VoiceSessionEvent
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.VoiceSessionEvent} VoiceSessionEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            VoiceSessionEvent.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.VoiceSessionEvent();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.event = reader.int32();
                            break;
                        }
                    case 2: {
                            message.state = reader.int32();
                            break;
                        }
                    case 3: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 4: {
                            message.turnIds = $root.fluent_audio.v1.TurnIds.decode(reader, reader.uint32(), undefined, long + 1);
                            break;
                        }
                    case 5: {
                            message.message = reader.string();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes a VoiceSessionEvent message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.VoiceSessionEvent
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.VoiceSessionEvent} VoiceSessionEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            VoiceSessionEvent.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a VoiceSessionEvent message.
             * @function verify
             * @memberof fluent_audio.v1.VoiceSessionEvent
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            VoiceSessionEvent.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                var properties = {};
                if (message.event != null && Object.hasOwnProperty.call(message, "event"))
                    switch (message.event) {
                    default:
                        return "event: enum value expected";
                    case 0:
                    case 1:
                    case 2:
                    case 3:
                    case 4:
                    case 5:
                    case 6:
                    case 7:
                    case 8:
                        break;
                    }
                if (message.state != null && Object.hasOwnProperty.call(message, "state"))
                    switch (message.state) {
                    default:
                        return "state: enum value expected";
                    case 0:
                    case 1:
                    case 2:
                    case 3:
                    case 4:
                    case 5:
                    case 6:
                    case 7:
                    case 8:
                    case 9:
                        break;
                    }
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.turnIds != null && Object.hasOwnProperty.call(message, "turnIds")) {
                    var error = $root.fluent_audio.v1.TurnIds.verify(message.turnIds, long + 1);
                    if (error)
                        return "turnIds." + error;
                }
                if (message.message != null && Object.hasOwnProperty.call(message, "message")) {
                    properties._message = 1;
                    if (!$util.isString(message.message))
                        return "message: string expected";
                }
                return null;
            };

            /**
             * Creates a VoiceSessionEvent message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.VoiceSessionEvent
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.VoiceSessionEvent} VoiceSessionEvent
             */
            VoiceSessionEvent.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.VoiceSessionEvent)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.VoiceSessionEvent: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.VoiceSessionEvent();
                switch (object.event) {
                default:
                    if (typeof object.event === "number") {
                        message.event = object.event;
                        break;
                    }
                    break;
                case "VOICE_SESSION_EVENT_KIND_UNSPECIFIED":
                case 0:
                    message.event = 0;
                    break;
                case "VOICE_SESSION_EVENT_KIND_SESSION_STARTED":
                case 1:
                    message.event = 1;
                    break;
                case "VOICE_SESSION_EVENT_KIND_STATE_CHANGED":
                case 2:
                    message.event = 2;
                    break;
                case "VOICE_SESSION_EVENT_KIND_USER_TURN_STARTED":
                case 3:
                    message.event = 3;
                    break;
                case "VOICE_SESSION_EVENT_KIND_USER_TURN_FINALIZED":
                case 4:
                    message.event = 4;
                    break;
                case "VOICE_SESSION_EVENT_KIND_ASSISTANT_TURN_STARTED":
                case 5:
                    message.event = 5;
                    break;
                case "VOICE_SESSION_EVENT_KIND_ASSISTANT_TURN_COMPLETED":
                case 6:
                    message.event = 6;
                    break;
                case "VOICE_SESSION_EVENT_KIND_SESSION_CLOSED":
                case 7:
                    message.event = 7;
                    break;
                case "VOICE_SESSION_EVENT_KIND_ERROR":
                case 8:
                    message.event = 8;
                    break;
                }
                switch (object.state) {
                default:
                    if (typeof object.state === "number") {
                        message.state = object.state;
                        break;
                    }
                    break;
                case "VOICE_SESSION_STATE_UNSPECIFIED":
                case 0:
                    message.state = 0;
                    break;
                case "VOICE_SESSION_STATE_IDLE":
                case 1:
                    message.state = 1;
                    break;
                case "VOICE_SESSION_STATE_LISTENING":
                case 2:
                    message.state = 2;
                    break;
                case "VOICE_SESSION_STATE_USER_SPEAKING":
                case 3:
                    message.state = 3;
                    break;
                case "VOICE_SESSION_STATE_TRANSCRIBING":
                case 4:
                    message.state = 4;
                    break;
                case "VOICE_SESSION_STATE_THINKING":
                case 5:
                    message.state = 5;
                    break;
                case "VOICE_SESSION_STATE_SPEAKING":
                case 6:
                    message.state = 6;
                    break;
                case "VOICE_SESSION_STATE_INTERRUPTED":
                case 7:
                    message.state = 7;
                    break;
                case "VOICE_SESSION_STATE_CLOSED":
                case 8:
                    message.state = 8;
                    break;
                case "VOICE_SESSION_STATE_ERROR":
                case 9:
                    message.state = 9;
                    break;
                }
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.turnIds != null) {
                    if (!$util.isObject(object.turnIds))
                        throw TypeError(".fluent_audio.v1.VoiceSessionEvent.turnIds: object expected");
                    message.turnIds = $root.fluent_audio.v1.TurnIds.fromObject(object.turnIds, long + 1);
                }
                if (object.message != null)
                    message.message = String(object.message);
                return message;
            };

            /**
             * Creates a plain object from a VoiceSessionEvent message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.VoiceSessionEvent
             * @static
             * @param {fluent_audio.v1.VoiceSessionEvent} message VoiceSessionEvent
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            VoiceSessionEvent.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.event = options.enums === String ? "VOICE_SESSION_EVENT_KIND_UNSPECIFIED" : 0;
                    object.state = options.enums === String ? "VOICE_SESSION_STATE_UNSPECIFIED" : 0;
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    object.turnIds = null;
                }
                if (message.event != null && Object.hasOwnProperty.call(message, "event"))
                    object.event = options.enums === String ? $root.fluent_audio.v1.VoiceSessionEventKind[message.event] === undefined ? message.event : $root.fluent_audio.v1.VoiceSessionEventKind[message.event] : message.event;
                if (message.state != null && Object.hasOwnProperty.call(message, "state"))
                    object.state = options.enums === String ? $root.fluent_audio.v1.VoiceSessionState[message.state] === undefined ? message.state : $root.fluent_audio.v1.VoiceSessionState[message.state] : message.state;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.turnIds != null && Object.hasOwnProperty.call(message, "turnIds"))
                    object.turnIds = $root.fluent_audio.v1.TurnIds.toObject(message.turnIds, options, q + 1);
                if (message.message != null && Object.hasOwnProperty.call(message, "message")) {
                    object.message = message.message;
                    if (options.oneofs)
                        object._message = "message";
                }
                return object;
            };

            /**
             * Converts this VoiceSessionEvent to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.VoiceSessionEvent
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            VoiceSessionEvent.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for VoiceSessionEvent
             * @function getTypeUrl
             * @memberof fluent_audio.v1.VoiceSessionEvent
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            VoiceSessionEvent.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.VoiceSessionEvent";
            };

            return VoiceSessionEvent;
        })();

        /**
         * PlaybackCommandKind enum.
         * @name fluent_audio.v1.PlaybackCommandKind
         * @enum {number}
         * @property {number} PLAYBACK_COMMAND_KIND_UNSPECIFIED=0 PLAYBACK_COMMAND_KIND_UNSPECIFIED value
         * @property {number} PLAYBACK_COMMAND_KIND_STOP=1 PLAYBACK_COMMAND_KIND_STOP value
         * @property {number} PLAYBACK_COMMAND_KIND_PAUSE=2 PLAYBACK_COMMAND_KIND_PAUSE value
         * @property {number} PLAYBACK_COMMAND_KIND_RESUME=3 PLAYBACK_COMMAND_KIND_RESUME value
         * @property {number} PLAYBACK_COMMAND_KIND_CLEAR=4 PLAYBACK_COMMAND_KIND_CLEAR value
         */
        v1.PlaybackCommandKind = (function() {
            var valuesById = {}, values = Object.create(valuesById);
            values[valuesById[0] = "PLAYBACK_COMMAND_KIND_UNSPECIFIED"] = 0;
            values[valuesById[1] = "PLAYBACK_COMMAND_KIND_STOP"] = 1;
            values[valuesById[2] = "PLAYBACK_COMMAND_KIND_PAUSE"] = 2;
            values[valuesById[3] = "PLAYBACK_COMMAND_KIND_RESUME"] = 3;
            values[valuesById[4] = "PLAYBACK_COMMAND_KIND_CLEAR"] = 4;
            return values;
        })();

        /**
         * PlaybackStateKind enum.
         * @name fluent_audio.v1.PlaybackStateKind
         * @enum {number}
         * @property {number} PLAYBACK_STATE_KIND_UNSPECIFIED=0 PLAYBACK_STATE_KIND_UNSPECIFIED value
         * @property {number} PLAYBACK_STATE_KIND_QUEUED=1 PLAYBACK_STATE_KIND_QUEUED value
         * @property {number} PLAYBACK_STATE_KIND_PLAYING=2 PLAYBACK_STATE_KIND_PLAYING value
         * @property {number} PLAYBACK_STATE_KIND_PAUSED=3 PLAYBACK_STATE_KIND_PAUSED value
         * @property {number} PLAYBACK_STATE_KIND_STOPPED=4 PLAYBACK_STATE_KIND_STOPPED value
         * @property {number} PLAYBACK_STATE_KIND_COMPLETED=5 PLAYBACK_STATE_KIND_COMPLETED value
         * @property {number} PLAYBACK_STATE_KIND_CANCELLED=6 PLAYBACK_STATE_KIND_CANCELLED value
         * @property {number} PLAYBACK_STATE_KIND_FAILED=7 PLAYBACK_STATE_KIND_FAILED value
         */
        v1.PlaybackStateKind = (function() {
            var valuesById = {}, values = Object.create(valuesById);
            values[valuesById[0] = "PLAYBACK_STATE_KIND_UNSPECIFIED"] = 0;
            values[valuesById[1] = "PLAYBACK_STATE_KIND_QUEUED"] = 1;
            values[valuesById[2] = "PLAYBACK_STATE_KIND_PLAYING"] = 2;
            values[valuesById[3] = "PLAYBACK_STATE_KIND_PAUSED"] = 3;
            values[valuesById[4] = "PLAYBACK_STATE_KIND_STOPPED"] = 4;
            values[valuesById[5] = "PLAYBACK_STATE_KIND_COMPLETED"] = 5;
            values[valuesById[6] = "PLAYBACK_STATE_KIND_CANCELLED"] = 6;
            values[valuesById[7] = "PLAYBACK_STATE_KIND_FAILED"] = 7;
            return values;
        })();

        /**
         * PlaybackDoneStatus enum.
         * @name fluent_audio.v1.PlaybackDoneStatus
         * @enum {number}
         * @property {number} PLAYBACK_DONE_STATUS_UNSPECIFIED=0 PLAYBACK_DONE_STATUS_UNSPECIFIED value
         * @property {number} PLAYBACK_DONE_STATUS_COMPLETED=1 PLAYBACK_DONE_STATUS_COMPLETED value
         * @property {number} PLAYBACK_DONE_STATUS_STOPPED=2 PLAYBACK_DONE_STATUS_STOPPED value
         * @property {number} PLAYBACK_DONE_STATUS_CANCELLED=3 PLAYBACK_DONE_STATUS_CANCELLED value
         * @property {number} PLAYBACK_DONE_STATUS_FAILED=4 PLAYBACK_DONE_STATUS_FAILED value
         */
        v1.PlaybackDoneStatus = (function() {
            var valuesById = {}, values = Object.create(valuesById);
            values[valuesById[0] = "PLAYBACK_DONE_STATUS_UNSPECIFIED"] = 0;
            values[valuesById[1] = "PLAYBACK_DONE_STATUS_COMPLETED"] = 1;
            values[valuesById[2] = "PLAYBACK_DONE_STATUS_STOPPED"] = 2;
            values[valuesById[3] = "PLAYBACK_DONE_STATUS_CANCELLED"] = 3;
            values[valuesById[4] = "PLAYBACK_DONE_STATUS_FAILED"] = 4;
            return values;
        })();

        v1.PlaybackCommand = (function() {

            /**
             * Properties of a PlaybackCommand.
             * @memberof fluent_audio.v1
             * @interface IPlaybackCommand
             * @property {fluent_audio.v1.PlaybackCommandKind|null} [command] PlaybackCommand command
             * @property {string|null} [requestId] PlaybackCommand requestId
             * @property {string|null} [streamId] PlaybackCommand streamId
             * @property {number|Long|null} [seq] PlaybackCommand seq
             */

            /**
             * Constructs a new PlaybackCommand.
             * @memberof fluent_audio.v1
             * @classdesc Represents a PlaybackCommand.
             * @implements IPlaybackCommand
             * @constructor
             * @param {fluent_audio.v1.IPlaybackCommand=} [properties] Properties to set
             */
            function PlaybackCommand(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * PlaybackCommand command.
             * @member {fluent_audio.v1.PlaybackCommandKind} command
             * @memberof fluent_audio.v1.PlaybackCommand
             * @instance
             */
            PlaybackCommand.prototype.command = 0;

            /**
             * PlaybackCommand requestId.
             * @member {string} requestId
             * @memberof fluent_audio.v1.PlaybackCommand
             * @instance
             */
            PlaybackCommand.prototype.requestId = "";

            /**
             * PlaybackCommand streamId.
             * @member {string} streamId
             * @memberof fluent_audio.v1.PlaybackCommand
             * @instance
             */
            PlaybackCommand.prototype.streamId = "";

            /**
             * PlaybackCommand seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.PlaybackCommand
             * @instance
             */
            PlaybackCommand.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * Creates a new PlaybackCommand instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.PlaybackCommand
             * @static
             * @param {fluent_audio.v1.IPlaybackCommand=} [properties] Properties to set
             * @returns {fluent_audio.v1.PlaybackCommand} PlaybackCommand instance
             */
            PlaybackCommand.create = function create(properties) {
                return new PlaybackCommand(properties);
            };

            /**
             * Encodes the specified PlaybackCommand message. Does not implicitly {@link fluent_audio.v1.PlaybackCommand.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.PlaybackCommand
             * @static
             * @param {fluent_audio.v1.IPlaybackCommand} message PlaybackCommand message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            PlaybackCommand.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.command != null && Object.hasOwnProperty.call(message, "command"))
                    writer.uint32(/* id 1, wireType 0 =*/8).int32(message.command);
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.requestId);
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.streamId);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.seq);
                return writer;
            };

            /**
             * Encodes the specified PlaybackCommand message, length delimited. Does not implicitly {@link fluent_audio.v1.PlaybackCommand.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.PlaybackCommand
             * @static
             * @param {fluent_audio.v1.IPlaybackCommand} message PlaybackCommand message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            PlaybackCommand.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes a PlaybackCommand message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.PlaybackCommand
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.PlaybackCommand} PlaybackCommand
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            PlaybackCommand.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.PlaybackCommand();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.command = reader.int32();
                            break;
                        }
                    case 2: {
                            message.requestId = reader.string();
                            break;
                        }
                    case 3: {
                            message.streamId = reader.string();
                            break;
                        }
                    case 4: {
                            message.seq = reader.uint64();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes a PlaybackCommand message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.PlaybackCommand
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.PlaybackCommand} PlaybackCommand
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            PlaybackCommand.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a PlaybackCommand message.
             * @function verify
             * @memberof fluent_audio.v1.PlaybackCommand
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            PlaybackCommand.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.command != null && Object.hasOwnProperty.call(message, "command"))
                    switch (message.command) {
                    default:
                        return "command: enum value expected";
                    case 0:
                    case 1:
                    case 2:
                    case 3:
                    case 4:
                        break;
                    }
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    if (!$util.isString(message.requestId))
                        return "requestId: string expected";
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    if (!$util.isString(message.streamId))
                        return "streamId: string expected";
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                return null;
            };

            /**
             * Creates a PlaybackCommand message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.PlaybackCommand
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.PlaybackCommand} PlaybackCommand
             */
            PlaybackCommand.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.PlaybackCommand)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.PlaybackCommand: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.PlaybackCommand();
                switch (object.command) {
                default:
                    if (typeof object.command === "number") {
                        message.command = object.command;
                        break;
                    }
                    break;
                case "PLAYBACK_COMMAND_KIND_UNSPECIFIED":
                case 0:
                    message.command = 0;
                    break;
                case "PLAYBACK_COMMAND_KIND_STOP":
                case 1:
                    message.command = 1;
                    break;
                case "PLAYBACK_COMMAND_KIND_PAUSE":
                case 2:
                    message.command = 2;
                    break;
                case "PLAYBACK_COMMAND_KIND_RESUME":
                case 3:
                    message.command = 3;
                    break;
                case "PLAYBACK_COMMAND_KIND_CLEAR":
                case 4:
                    message.command = 4;
                    break;
                }
                if (object.requestId != null)
                    message.requestId = String(object.requestId);
                if (object.streamId != null)
                    message.streamId = String(object.streamId);
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                return message;
            };

            /**
             * Creates a plain object from a PlaybackCommand message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.PlaybackCommand
             * @static
             * @param {fluent_audio.v1.PlaybackCommand} message PlaybackCommand
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            PlaybackCommand.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.command = options.enums === String ? "PLAYBACK_COMMAND_KIND_UNSPECIFIED" : 0;
                    object.requestId = "";
                    object.streamId = "";
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                }
                if (message.command != null && Object.hasOwnProperty.call(message, "command"))
                    object.command = options.enums === String ? $root.fluent_audio.v1.PlaybackCommandKind[message.command] === undefined ? message.command : $root.fluent_audio.v1.PlaybackCommandKind[message.command] : message.command;
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    object.requestId = message.requestId;
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    object.streamId = message.streamId;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                return object;
            };

            /**
             * Converts this PlaybackCommand to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.PlaybackCommand
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            PlaybackCommand.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for PlaybackCommand
             * @function getTypeUrl
             * @memberof fluent_audio.v1.PlaybackCommand
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            PlaybackCommand.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.PlaybackCommand";
            };

            return PlaybackCommand;
        })();

        v1.PlaybackState = (function() {

            /**
             * Properties of a PlaybackState.
             * @memberof fluent_audio.v1
             * @interface IPlaybackState
             * @property {string|null} [requestId] PlaybackState requestId
             * @property {string|null} [sessionId] PlaybackState sessionId
             * @property {string|null} [userTurnId] PlaybackState userTurnId
             * @property {string|null} [streamId] PlaybackState streamId
             * @property {fluent_audio.v1.PlaybackStateKind|null} [state] PlaybackState state
             * @property {number|Long|null} [seq] PlaybackState seq
             * @property {number|Long|null} [playedFrames] PlaybackState playedFrames
             * @property {string|null} [reason] PlaybackState reason
             */

            /**
             * Constructs a new PlaybackState.
             * @memberof fluent_audio.v1
             * @classdesc Represents a PlaybackState.
             * @implements IPlaybackState
             * @constructor
             * @param {fluent_audio.v1.IPlaybackState=} [properties] Properties to set
             */
            function PlaybackState(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * PlaybackState requestId.
             * @member {string} requestId
             * @memberof fluent_audio.v1.PlaybackState
             * @instance
             */
            PlaybackState.prototype.requestId = "";

            /**
             * PlaybackState sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.PlaybackState
             * @instance
             */
            PlaybackState.prototype.sessionId = "";

            /**
             * PlaybackState userTurnId.
             * @member {string} userTurnId
             * @memberof fluent_audio.v1.PlaybackState
             * @instance
             */
            PlaybackState.prototype.userTurnId = "";

            /**
             * PlaybackState streamId.
             * @member {string} streamId
             * @memberof fluent_audio.v1.PlaybackState
             * @instance
             */
            PlaybackState.prototype.streamId = "";

            /**
             * PlaybackState state.
             * @member {fluent_audio.v1.PlaybackStateKind} state
             * @memberof fluent_audio.v1.PlaybackState
             * @instance
             */
            PlaybackState.prototype.state = 0;

            /**
             * PlaybackState seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.PlaybackState
             * @instance
             */
            PlaybackState.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * PlaybackState playedFrames.
             * @member {number|Long} playedFrames
             * @memberof fluent_audio.v1.PlaybackState
             * @instance
             */
            PlaybackState.prototype.playedFrames = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * PlaybackState reason.
             * @member {string|null|undefined} reason
             * @memberof fluent_audio.v1.PlaybackState
             * @instance
             */
            PlaybackState.prototype.reason = null;

            // OneOf field names bound to virtual getters and setters
            var $oneOfFields;

            // Virtual OneOf for proto3 optional field
            Object.defineProperty(PlaybackState.prototype, "_reason", {
                get: $util.oneOfGetter($oneOfFields = ["reason"]),
                set: $util.oneOfSetter($oneOfFields)
            });

            /**
             * Creates a new PlaybackState instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.PlaybackState
             * @static
             * @param {fluent_audio.v1.IPlaybackState=} [properties] Properties to set
             * @returns {fluent_audio.v1.PlaybackState} PlaybackState instance
             */
            PlaybackState.create = function create(properties) {
                return new PlaybackState(properties);
            };

            /**
             * Encodes the specified PlaybackState message. Does not implicitly {@link fluent_audio.v1.PlaybackState.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.PlaybackState
             * @static
             * @param {fluent_audio.v1.IPlaybackState} message PlaybackState message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            PlaybackState.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.requestId);
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.sessionId);
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.userTurnId);
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    writer.uint32(/* id 4, wireType 2 =*/34).string(message.streamId);
                if (message.state != null && Object.hasOwnProperty.call(message, "state"))
                    writer.uint32(/* id 5, wireType 0 =*/40).int32(message.state);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 6, wireType 0 =*/48).uint64(message.seq);
                if (message.playedFrames != null && Object.hasOwnProperty.call(message, "playedFrames"))
                    writer.uint32(/* id 7, wireType 0 =*/56).uint64(message.playedFrames);
                if (message.reason != null && Object.hasOwnProperty.call(message, "reason"))
                    writer.uint32(/* id 8, wireType 2 =*/66).string(message.reason);
                return writer;
            };

            /**
             * Encodes the specified PlaybackState message, length delimited. Does not implicitly {@link fluent_audio.v1.PlaybackState.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.PlaybackState
             * @static
             * @param {fluent_audio.v1.IPlaybackState} message PlaybackState message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            PlaybackState.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes a PlaybackState message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.PlaybackState
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.PlaybackState} PlaybackState
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            PlaybackState.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.PlaybackState();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.requestId = reader.string();
                            break;
                        }
                    case 2: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 3: {
                            message.userTurnId = reader.string();
                            break;
                        }
                    case 4: {
                            message.streamId = reader.string();
                            break;
                        }
                    case 5: {
                            message.state = reader.int32();
                            break;
                        }
                    case 6: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 7: {
                            message.playedFrames = reader.uint64();
                            break;
                        }
                    case 8: {
                            message.reason = reader.string();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes a PlaybackState message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.PlaybackState
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.PlaybackState} PlaybackState
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            PlaybackState.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a PlaybackState message.
             * @function verify
             * @memberof fluent_audio.v1.PlaybackState
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            PlaybackState.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                var properties = {};
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    if (!$util.isString(message.requestId))
                        return "requestId: string expected";
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    if (!$util.isString(message.userTurnId))
                        return "userTurnId: string expected";
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    if (!$util.isString(message.streamId))
                        return "streamId: string expected";
                if (message.state != null && Object.hasOwnProperty.call(message, "state"))
                    switch (message.state) {
                    default:
                        return "state: enum value expected";
                    case 0:
                    case 1:
                    case 2:
                    case 3:
                    case 4:
                    case 5:
                    case 6:
                    case 7:
                        break;
                    }
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.playedFrames != null && Object.hasOwnProperty.call(message, "playedFrames"))
                    if (!$util.isInteger(message.playedFrames) && !(message.playedFrames && $util.isInteger(message.playedFrames.low) && $util.isInteger(message.playedFrames.high)))
                        return "playedFrames: integer|Long expected";
                if (message.reason != null && Object.hasOwnProperty.call(message, "reason")) {
                    properties._reason = 1;
                    if (!$util.isString(message.reason))
                        return "reason: string expected";
                }
                return null;
            };

            /**
             * Creates a PlaybackState message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.PlaybackState
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.PlaybackState} PlaybackState
             */
            PlaybackState.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.PlaybackState)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.PlaybackState: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.PlaybackState();
                if (object.requestId != null)
                    message.requestId = String(object.requestId);
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.userTurnId != null)
                    message.userTurnId = String(object.userTurnId);
                if (object.streamId != null)
                    message.streamId = String(object.streamId);
                switch (object.state) {
                default:
                    if (typeof object.state === "number") {
                        message.state = object.state;
                        break;
                    }
                    break;
                case "PLAYBACK_STATE_KIND_UNSPECIFIED":
                case 0:
                    message.state = 0;
                    break;
                case "PLAYBACK_STATE_KIND_QUEUED":
                case 1:
                    message.state = 1;
                    break;
                case "PLAYBACK_STATE_KIND_PLAYING":
                case 2:
                    message.state = 2;
                    break;
                case "PLAYBACK_STATE_KIND_PAUSED":
                case 3:
                    message.state = 3;
                    break;
                case "PLAYBACK_STATE_KIND_STOPPED":
                case 4:
                    message.state = 4;
                    break;
                case "PLAYBACK_STATE_KIND_COMPLETED":
                case 5:
                    message.state = 5;
                    break;
                case "PLAYBACK_STATE_KIND_CANCELLED":
                case 6:
                    message.state = 6;
                    break;
                case "PLAYBACK_STATE_KIND_FAILED":
                case 7:
                    message.state = 7;
                    break;
                }
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.playedFrames != null)
                    if ($util.Long)
                        message.playedFrames = $util.Long.fromValue(object.playedFrames, true);
                    else if (typeof object.playedFrames === "string")
                        message.playedFrames = parseInt(object.playedFrames, 10);
                    else if (typeof object.playedFrames === "number")
                        message.playedFrames = object.playedFrames;
                    else if (typeof object.playedFrames === "object")
                        message.playedFrames = new $util.LongBits(object.playedFrames.low >>> 0, object.playedFrames.high >>> 0).toNumber(true);
                if (object.reason != null)
                    message.reason = String(object.reason);
                return message;
            };

            /**
             * Creates a plain object from a PlaybackState message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.PlaybackState
             * @static
             * @param {fluent_audio.v1.PlaybackState} message PlaybackState
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            PlaybackState.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.requestId = "";
                    object.sessionId = "";
                    object.userTurnId = "";
                    object.streamId = "";
                    object.state = options.enums === String ? "PLAYBACK_STATE_KIND_UNSPECIFIED" : 0;
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.playedFrames = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.playedFrames = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                }
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    object.requestId = message.requestId;
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    object.userTurnId = message.userTurnId;
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    object.streamId = message.streamId;
                if (message.state != null && Object.hasOwnProperty.call(message, "state"))
                    object.state = options.enums === String ? $root.fluent_audio.v1.PlaybackStateKind[message.state] === undefined ? message.state : $root.fluent_audio.v1.PlaybackStateKind[message.state] : message.state;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.playedFrames != null && Object.hasOwnProperty.call(message, "playedFrames"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.playedFrames = typeof message.playedFrames === "number" ? BigInt(message.playedFrames) : $util.Long.fromBits(message.playedFrames.low >>> 0, message.playedFrames.high >>> 0, true).toBigInt();
                    else if (typeof message.playedFrames === "number")
                        object.playedFrames = options.longs === String ? String(message.playedFrames) : message.playedFrames;
                    else
                        object.playedFrames = options.longs === String ? $util.Long.prototype.toString.call(message.playedFrames) : options.longs === Number ? new $util.LongBits(message.playedFrames.low >>> 0, message.playedFrames.high >>> 0).toNumber(true) : message.playedFrames;
                if (message.reason != null && Object.hasOwnProperty.call(message, "reason")) {
                    object.reason = message.reason;
                    if (options.oneofs)
                        object._reason = "reason";
                }
                return object;
            };

            /**
             * Converts this PlaybackState to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.PlaybackState
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            PlaybackState.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for PlaybackState
             * @function getTypeUrl
             * @memberof fluent_audio.v1.PlaybackState
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            PlaybackState.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.PlaybackState";
            };

            return PlaybackState;
        })();

        v1.PlaybackDone = (function() {

            /**
             * Properties of a PlaybackDone.
             * @memberof fluent_audio.v1
             * @interface IPlaybackDone
             * @property {string|null} [requestId] PlaybackDone requestId
             * @property {string|null} [sessionId] PlaybackDone sessionId
             * @property {string|null} [userTurnId] PlaybackDone userTurnId
             * @property {string|null} [streamId] PlaybackDone streamId
             * @property {fluent_audio.v1.PlaybackDoneStatus|null} [status] PlaybackDone status
             * @property {number|Long|null} [finalSequence] PlaybackDone finalSequence
             * @property {number|Long|null} [totalFrames] PlaybackDone totalFrames
             * @property {string|null} [reason] PlaybackDone reason
             */

            /**
             * Constructs a new PlaybackDone.
             * @memberof fluent_audio.v1
             * @classdesc Represents a PlaybackDone.
             * @implements IPlaybackDone
             * @constructor
             * @param {fluent_audio.v1.IPlaybackDone=} [properties] Properties to set
             */
            function PlaybackDone(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * PlaybackDone requestId.
             * @member {string} requestId
             * @memberof fluent_audio.v1.PlaybackDone
             * @instance
             */
            PlaybackDone.prototype.requestId = "";

            /**
             * PlaybackDone sessionId.
             * @member {string} sessionId
             * @memberof fluent_audio.v1.PlaybackDone
             * @instance
             */
            PlaybackDone.prototype.sessionId = "";

            /**
             * PlaybackDone userTurnId.
             * @member {string} userTurnId
             * @memberof fluent_audio.v1.PlaybackDone
             * @instance
             */
            PlaybackDone.prototype.userTurnId = "";

            /**
             * PlaybackDone streamId.
             * @member {string} streamId
             * @memberof fluent_audio.v1.PlaybackDone
             * @instance
             */
            PlaybackDone.prototype.streamId = "";

            /**
             * PlaybackDone status.
             * @member {fluent_audio.v1.PlaybackDoneStatus} status
             * @memberof fluent_audio.v1.PlaybackDone
             * @instance
             */
            PlaybackDone.prototype.status = 0;

            /**
             * PlaybackDone finalSequence.
             * @member {number|Long|null|undefined} finalSequence
             * @memberof fluent_audio.v1.PlaybackDone
             * @instance
             */
            PlaybackDone.prototype.finalSequence = null;

            /**
             * PlaybackDone totalFrames.
             * @member {number|Long|null|undefined} totalFrames
             * @memberof fluent_audio.v1.PlaybackDone
             * @instance
             */
            PlaybackDone.prototype.totalFrames = null;

            /**
             * PlaybackDone reason.
             * @member {string|null|undefined} reason
             * @memberof fluent_audio.v1.PlaybackDone
             * @instance
             */
            PlaybackDone.prototype.reason = null;

            // OneOf field names bound to virtual getters and setters
            var $oneOfFields;

            // Virtual OneOf for proto3 optional field
            Object.defineProperty(PlaybackDone.prototype, "_finalSequence", {
                get: $util.oneOfGetter($oneOfFields = ["finalSequence"]),
                set: $util.oneOfSetter($oneOfFields)
            });

            // Virtual OneOf for proto3 optional field
            Object.defineProperty(PlaybackDone.prototype, "_totalFrames", {
                get: $util.oneOfGetter($oneOfFields = ["totalFrames"]),
                set: $util.oneOfSetter($oneOfFields)
            });

            // Virtual OneOf for proto3 optional field
            Object.defineProperty(PlaybackDone.prototype, "_reason", {
                get: $util.oneOfGetter($oneOfFields = ["reason"]),
                set: $util.oneOfSetter($oneOfFields)
            });

            /**
             * Creates a new PlaybackDone instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.PlaybackDone
             * @static
             * @param {fluent_audio.v1.IPlaybackDone=} [properties] Properties to set
             * @returns {fluent_audio.v1.PlaybackDone} PlaybackDone instance
             */
            PlaybackDone.create = function create(properties) {
                return new PlaybackDone(properties);
            };

            /**
             * Encodes the specified PlaybackDone message. Does not implicitly {@link fluent_audio.v1.PlaybackDone.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.PlaybackDone
             * @static
             * @param {fluent_audio.v1.IPlaybackDone} message PlaybackDone message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            PlaybackDone.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.requestId);
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.sessionId);
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.userTurnId);
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    writer.uint32(/* id 4, wireType 2 =*/34).string(message.streamId);
                if (message.status != null && Object.hasOwnProperty.call(message, "status"))
                    writer.uint32(/* id 5, wireType 0 =*/40).int32(message.status);
                if (message.finalSequence != null && Object.hasOwnProperty.call(message, "finalSequence"))
                    writer.uint32(/* id 6, wireType 0 =*/48).uint64(message.finalSequence);
                if (message.totalFrames != null && Object.hasOwnProperty.call(message, "totalFrames"))
                    writer.uint32(/* id 7, wireType 0 =*/56).uint64(message.totalFrames);
                if (message.reason != null && Object.hasOwnProperty.call(message, "reason"))
                    writer.uint32(/* id 8, wireType 2 =*/66).string(message.reason);
                return writer;
            };

            /**
             * Encodes the specified PlaybackDone message, length delimited. Does not implicitly {@link fluent_audio.v1.PlaybackDone.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.PlaybackDone
             * @static
             * @param {fluent_audio.v1.IPlaybackDone} message PlaybackDone message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            PlaybackDone.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes a PlaybackDone message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.PlaybackDone
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.PlaybackDone} PlaybackDone
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            PlaybackDone.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.PlaybackDone();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.requestId = reader.string();
                            break;
                        }
                    case 2: {
                            message.sessionId = reader.string();
                            break;
                        }
                    case 3: {
                            message.userTurnId = reader.string();
                            break;
                        }
                    case 4: {
                            message.streamId = reader.string();
                            break;
                        }
                    case 5: {
                            message.status = reader.int32();
                            break;
                        }
                    case 6: {
                            message.finalSequence = reader.uint64();
                            break;
                        }
                    case 7: {
                            message.totalFrames = reader.uint64();
                            break;
                        }
                    case 8: {
                            message.reason = reader.string();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes a PlaybackDone message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.PlaybackDone
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.PlaybackDone} PlaybackDone
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            PlaybackDone.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a PlaybackDone message.
             * @function verify
             * @memberof fluent_audio.v1.PlaybackDone
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            PlaybackDone.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                var properties = {};
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    if (!$util.isString(message.requestId))
                        return "requestId: string expected";
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    if (!$util.isString(message.sessionId))
                        return "sessionId: string expected";
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    if (!$util.isString(message.userTurnId))
                        return "userTurnId: string expected";
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    if (!$util.isString(message.streamId))
                        return "streamId: string expected";
                if (message.status != null && Object.hasOwnProperty.call(message, "status"))
                    switch (message.status) {
                    default:
                        return "status: enum value expected";
                    case 0:
                    case 1:
                    case 2:
                    case 3:
                    case 4:
                        break;
                    }
                if (message.finalSequence != null && Object.hasOwnProperty.call(message, "finalSequence")) {
                    properties._finalSequence = 1;
                    if (!$util.isInteger(message.finalSequence) && !(message.finalSequence && $util.isInteger(message.finalSequence.low) && $util.isInteger(message.finalSequence.high)))
                        return "finalSequence: integer|Long expected";
                }
                if (message.totalFrames != null && Object.hasOwnProperty.call(message, "totalFrames")) {
                    properties._totalFrames = 1;
                    if (!$util.isInteger(message.totalFrames) && !(message.totalFrames && $util.isInteger(message.totalFrames.low) && $util.isInteger(message.totalFrames.high)))
                        return "totalFrames: integer|Long expected";
                }
                if (message.reason != null && Object.hasOwnProperty.call(message, "reason")) {
                    properties._reason = 1;
                    if (!$util.isString(message.reason))
                        return "reason: string expected";
                }
                return null;
            };

            /**
             * Creates a PlaybackDone message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.PlaybackDone
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.PlaybackDone} PlaybackDone
             */
            PlaybackDone.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.PlaybackDone)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.PlaybackDone: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.PlaybackDone();
                if (object.requestId != null)
                    message.requestId = String(object.requestId);
                if (object.sessionId != null)
                    message.sessionId = String(object.sessionId);
                if (object.userTurnId != null)
                    message.userTurnId = String(object.userTurnId);
                if (object.streamId != null)
                    message.streamId = String(object.streamId);
                switch (object.status) {
                default:
                    if (typeof object.status === "number") {
                        message.status = object.status;
                        break;
                    }
                    break;
                case "PLAYBACK_DONE_STATUS_UNSPECIFIED":
                case 0:
                    message.status = 0;
                    break;
                case "PLAYBACK_DONE_STATUS_COMPLETED":
                case 1:
                    message.status = 1;
                    break;
                case "PLAYBACK_DONE_STATUS_STOPPED":
                case 2:
                    message.status = 2;
                    break;
                case "PLAYBACK_DONE_STATUS_CANCELLED":
                case 3:
                    message.status = 3;
                    break;
                case "PLAYBACK_DONE_STATUS_FAILED":
                case 4:
                    message.status = 4;
                    break;
                }
                if (object.finalSequence != null)
                    if ($util.Long)
                        message.finalSequence = $util.Long.fromValue(object.finalSequence, true);
                    else if (typeof object.finalSequence === "string")
                        message.finalSequence = parseInt(object.finalSequence, 10);
                    else if (typeof object.finalSequence === "number")
                        message.finalSequence = object.finalSequence;
                    else if (typeof object.finalSequence === "object")
                        message.finalSequence = new $util.LongBits(object.finalSequence.low >>> 0, object.finalSequence.high >>> 0).toNumber(true);
                if (object.totalFrames != null)
                    if ($util.Long)
                        message.totalFrames = $util.Long.fromValue(object.totalFrames, true);
                    else if (typeof object.totalFrames === "string")
                        message.totalFrames = parseInt(object.totalFrames, 10);
                    else if (typeof object.totalFrames === "number")
                        message.totalFrames = object.totalFrames;
                    else if (typeof object.totalFrames === "object")
                        message.totalFrames = new $util.LongBits(object.totalFrames.low >>> 0, object.totalFrames.high >>> 0).toNumber(true);
                if (object.reason != null)
                    message.reason = String(object.reason);
                return message;
            };

            /**
             * Creates a plain object from a PlaybackDone message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.PlaybackDone
             * @static
             * @param {fluent_audio.v1.PlaybackDone} message PlaybackDone
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            PlaybackDone.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.requestId = "";
                    object.sessionId = "";
                    object.userTurnId = "";
                    object.streamId = "";
                    object.status = options.enums === String ? "PLAYBACK_DONE_STATUS_UNSPECIFIED" : 0;
                }
                if (message.requestId != null && Object.hasOwnProperty.call(message, "requestId"))
                    object.requestId = message.requestId;
                if (message.sessionId != null && Object.hasOwnProperty.call(message, "sessionId"))
                    object.sessionId = message.sessionId;
                if (message.userTurnId != null && Object.hasOwnProperty.call(message, "userTurnId"))
                    object.userTurnId = message.userTurnId;
                if (message.streamId != null && Object.hasOwnProperty.call(message, "streamId"))
                    object.streamId = message.streamId;
                if (message.status != null && Object.hasOwnProperty.call(message, "status"))
                    object.status = options.enums === String ? $root.fluent_audio.v1.PlaybackDoneStatus[message.status] === undefined ? message.status : $root.fluent_audio.v1.PlaybackDoneStatus[message.status] : message.status;
                if (message.finalSequence != null && Object.hasOwnProperty.call(message, "finalSequence")) {
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.finalSequence = typeof message.finalSequence === "number" ? BigInt(message.finalSequence) : $util.Long.fromBits(message.finalSequence.low >>> 0, message.finalSequence.high >>> 0, true).toBigInt();
                    else if (typeof message.finalSequence === "number")
                        object.finalSequence = options.longs === String ? String(message.finalSequence) : message.finalSequence;
                    else
                        object.finalSequence = options.longs === String ? $util.Long.prototype.toString.call(message.finalSequence) : options.longs === Number ? new $util.LongBits(message.finalSequence.low >>> 0, message.finalSequence.high >>> 0).toNumber(true) : message.finalSequence;
                    if (options.oneofs)
                        object._finalSequence = "finalSequence";
                }
                if (message.totalFrames != null && Object.hasOwnProperty.call(message, "totalFrames")) {
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.totalFrames = typeof message.totalFrames === "number" ? BigInt(message.totalFrames) : $util.Long.fromBits(message.totalFrames.low >>> 0, message.totalFrames.high >>> 0, true).toBigInt();
                    else if (typeof message.totalFrames === "number")
                        object.totalFrames = options.longs === String ? String(message.totalFrames) : message.totalFrames;
                    else
                        object.totalFrames = options.longs === String ? $util.Long.prototype.toString.call(message.totalFrames) : options.longs === Number ? new $util.LongBits(message.totalFrames.low >>> 0, message.totalFrames.high >>> 0).toNumber(true) : message.totalFrames;
                    if (options.oneofs)
                        object._totalFrames = "totalFrames";
                }
                if (message.reason != null && Object.hasOwnProperty.call(message, "reason")) {
                    object.reason = message.reason;
                    if (options.oneofs)
                        object._reason = "reason";
                }
                return object;
            };

            /**
             * Converts this PlaybackDone to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.PlaybackDone
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            PlaybackDone.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for PlaybackDone
             * @function getTypeUrl
             * @memberof fluent_audio.v1.PlaybackDone
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            PlaybackDone.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.PlaybackDone";
            };

            return PlaybackDone;
        })();

        /**
         * DiagnosticSeverity enum.
         * @name fluent_audio.v1.DiagnosticSeverity
         * @enum {number}
         * @property {number} DIAGNOSTIC_SEVERITY_UNSPECIFIED=0 DIAGNOSTIC_SEVERITY_UNSPECIFIED value
         * @property {number} DIAGNOSTIC_SEVERITY_OK=1 DIAGNOSTIC_SEVERITY_OK value
         * @property {number} DIAGNOSTIC_SEVERITY_WARN=2 DIAGNOSTIC_SEVERITY_WARN value
         * @property {number} DIAGNOSTIC_SEVERITY_ERROR=3 DIAGNOSTIC_SEVERITY_ERROR value
         * @property {number} DIAGNOSTIC_SEVERITY_FATAL=4 DIAGNOSTIC_SEVERITY_FATAL value
         */
        v1.DiagnosticSeverity = (function() {
            var valuesById = {}, values = Object.create(valuesById);
            values[valuesById[0] = "DIAGNOSTIC_SEVERITY_UNSPECIFIED"] = 0;
            values[valuesById[1] = "DIAGNOSTIC_SEVERITY_OK"] = 1;
            values[valuesById[2] = "DIAGNOSTIC_SEVERITY_WARN"] = 2;
            values[valuesById[3] = "DIAGNOSTIC_SEVERITY_ERROR"] = 3;
            values[valuesById[4] = "DIAGNOSTIC_SEVERITY_FATAL"] = 4;
            return values;
        })();

        /**
         * NodeState enum.
         * @name fluent_audio.v1.NodeState
         * @enum {number}
         * @property {number} NODE_STATE_UNSPECIFIED=0 NODE_STATE_UNSPECIFIED value
         * @property {number} NODE_STATE_STARTING=1 NODE_STATE_STARTING value
         * @property {number} NODE_STATE_READY=2 NODE_STATE_READY value
         * @property {number} NODE_STATE_RUNNING=3 NODE_STATE_RUNNING value
         * @property {number} NODE_STATE_DEGRADED=4 NODE_STATE_DEGRADED value
         * @property {number} NODE_STATE_STOPPING=5 NODE_STATE_STOPPING value
         * @property {number} NODE_STATE_STOPPED=6 NODE_STATE_STOPPED value
         * @property {number} NODE_STATE_FAILED=7 NODE_STATE_FAILED value
         */
        v1.NodeState = (function() {
            var valuesById = {}, values = Object.create(valuesById);
            values[valuesById[0] = "NODE_STATE_UNSPECIFIED"] = 0;
            values[valuesById[1] = "NODE_STATE_STARTING"] = 1;
            values[valuesById[2] = "NODE_STATE_READY"] = 2;
            values[valuesById[3] = "NODE_STATE_RUNNING"] = 3;
            values[valuesById[4] = "NODE_STATE_DEGRADED"] = 4;
            values[valuesById[5] = "NODE_STATE_STOPPING"] = 5;
            values[valuesById[6] = "NODE_STATE_STOPPED"] = 6;
            values[valuesById[7] = "NODE_STATE_FAILED"] = 7;
            return values;
        })();

        v1.NodeStatus = (function() {

            /**
             * Properties of a NodeStatus.
             * @memberof fluent_audio.v1
             * @interface INodeStatus
             * @property {string|null} [nodeId] NodeStatus nodeId
             * @property {fluent_audio.v1.NodeState|null} [state] NodeStatus state
             * @property {number|Long|null} [seq] NodeStatus seq
             * @property {number|Long|null} [observedTimeNs] NodeStatus observedTimeNs
             * @property {string|null} [message] NodeStatus message
             */

            /**
             * Constructs a new NodeStatus.
             * @memberof fluent_audio.v1
             * @classdesc Represents a NodeStatus.
             * @implements INodeStatus
             * @constructor
             * @param {fluent_audio.v1.INodeStatus=} [properties] Properties to set
             */
            function NodeStatus(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * NodeStatus nodeId.
             * @member {string} nodeId
             * @memberof fluent_audio.v1.NodeStatus
             * @instance
             */
            NodeStatus.prototype.nodeId = "";

            /**
             * NodeStatus state.
             * @member {fluent_audio.v1.NodeState} state
             * @memberof fluent_audio.v1.NodeStatus
             * @instance
             */
            NodeStatus.prototype.state = 0;

            /**
             * NodeStatus seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.NodeStatus
             * @instance
             */
            NodeStatus.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * NodeStatus observedTimeNs.
             * @member {number|Long} observedTimeNs
             * @memberof fluent_audio.v1.NodeStatus
             * @instance
             */
            NodeStatus.prototype.observedTimeNs = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * NodeStatus message.
             * @member {string|null|undefined} message
             * @memberof fluent_audio.v1.NodeStatus
             * @instance
             */
            NodeStatus.prototype.message = null;

            // OneOf field names bound to virtual getters and setters
            var $oneOfFields;

            // Virtual OneOf for proto3 optional field
            Object.defineProperty(NodeStatus.prototype, "_message", {
                get: $util.oneOfGetter($oneOfFields = ["message"]),
                set: $util.oneOfSetter($oneOfFields)
            });

            /**
             * Creates a new NodeStatus instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.NodeStatus
             * @static
             * @param {fluent_audio.v1.INodeStatus=} [properties] Properties to set
             * @returns {fluent_audio.v1.NodeStatus} NodeStatus instance
             */
            NodeStatus.create = function create(properties) {
                return new NodeStatus(properties);
            };

            /**
             * Encodes the specified NodeStatus message. Does not implicitly {@link fluent_audio.v1.NodeStatus.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.NodeStatus
             * @static
             * @param {fluent_audio.v1.INodeStatus} message NodeStatus message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            NodeStatus.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.nodeId != null && Object.hasOwnProperty.call(message, "nodeId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.nodeId);
                if (message.state != null && Object.hasOwnProperty.call(message, "state"))
                    writer.uint32(/* id 2, wireType 0 =*/16).int32(message.state);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 3, wireType 0 =*/24).uint64(message.seq);
                if (message.observedTimeNs != null && Object.hasOwnProperty.call(message, "observedTimeNs"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.observedTimeNs);
                if (message.message != null && Object.hasOwnProperty.call(message, "message"))
                    writer.uint32(/* id 5, wireType 2 =*/42).string(message.message);
                return writer;
            };

            /**
             * Encodes the specified NodeStatus message, length delimited. Does not implicitly {@link fluent_audio.v1.NodeStatus.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.NodeStatus
             * @static
             * @param {fluent_audio.v1.INodeStatus} message NodeStatus message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            NodeStatus.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes a NodeStatus message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.NodeStatus
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.NodeStatus} NodeStatus
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            NodeStatus.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.NodeStatus();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.nodeId = reader.string();
                            break;
                        }
                    case 2: {
                            message.state = reader.int32();
                            break;
                        }
                    case 3: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 4: {
                            message.observedTimeNs = reader.uint64();
                            break;
                        }
                    case 5: {
                            message.message = reader.string();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes a NodeStatus message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.NodeStatus
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.NodeStatus} NodeStatus
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            NodeStatus.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a NodeStatus message.
             * @function verify
             * @memberof fluent_audio.v1.NodeStatus
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            NodeStatus.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                var properties = {};
                if (message.nodeId != null && Object.hasOwnProperty.call(message, "nodeId"))
                    if (!$util.isString(message.nodeId))
                        return "nodeId: string expected";
                if (message.state != null && Object.hasOwnProperty.call(message, "state"))
                    switch (message.state) {
                    default:
                        return "state: enum value expected";
                    case 0:
                    case 1:
                    case 2:
                    case 3:
                    case 4:
                    case 5:
                    case 6:
                    case 7:
                        break;
                    }
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.observedTimeNs != null && Object.hasOwnProperty.call(message, "observedTimeNs"))
                    if (!$util.isInteger(message.observedTimeNs) && !(message.observedTimeNs && $util.isInteger(message.observedTimeNs.low) && $util.isInteger(message.observedTimeNs.high)))
                        return "observedTimeNs: integer|Long expected";
                if (message.message != null && Object.hasOwnProperty.call(message, "message")) {
                    properties._message = 1;
                    if (!$util.isString(message.message))
                        return "message: string expected";
                }
                return null;
            };

            /**
             * Creates a NodeStatus message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.NodeStatus
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.NodeStatus} NodeStatus
             */
            NodeStatus.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.NodeStatus)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.NodeStatus: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.NodeStatus();
                if (object.nodeId != null)
                    message.nodeId = String(object.nodeId);
                switch (object.state) {
                default:
                    if (typeof object.state === "number") {
                        message.state = object.state;
                        break;
                    }
                    break;
                case "NODE_STATE_UNSPECIFIED":
                case 0:
                    message.state = 0;
                    break;
                case "NODE_STATE_STARTING":
                case 1:
                    message.state = 1;
                    break;
                case "NODE_STATE_READY":
                case 2:
                    message.state = 2;
                    break;
                case "NODE_STATE_RUNNING":
                case 3:
                    message.state = 3;
                    break;
                case "NODE_STATE_DEGRADED":
                case 4:
                    message.state = 4;
                    break;
                case "NODE_STATE_STOPPING":
                case 5:
                    message.state = 5;
                    break;
                case "NODE_STATE_STOPPED":
                case 6:
                    message.state = 6;
                    break;
                case "NODE_STATE_FAILED":
                case 7:
                    message.state = 7;
                    break;
                }
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.observedTimeNs != null)
                    if ($util.Long)
                        message.observedTimeNs = $util.Long.fromValue(object.observedTimeNs, true);
                    else if (typeof object.observedTimeNs === "string")
                        message.observedTimeNs = parseInt(object.observedTimeNs, 10);
                    else if (typeof object.observedTimeNs === "number")
                        message.observedTimeNs = object.observedTimeNs;
                    else if (typeof object.observedTimeNs === "object")
                        message.observedTimeNs = new $util.LongBits(object.observedTimeNs.low >>> 0, object.observedTimeNs.high >>> 0).toNumber(true);
                if (object.message != null)
                    message.message = String(object.message);
                return message;
            };

            /**
             * Creates a plain object from a NodeStatus message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.NodeStatus
             * @static
             * @param {fluent_audio.v1.NodeStatus} message NodeStatus
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            NodeStatus.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.nodeId = "";
                    object.state = options.enums === String ? "NODE_STATE_UNSPECIFIED" : 0;
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.observedTimeNs = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.observedTimeNs = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                }
                if (message.nodeId != null && Object.hasOwnProperty.call(message, "nodeId"))
                    object.nodeId = message.nodeId;
                if (message.state != null && Object.hasOwnProperty.call(message, "state"))
                    object.state = options.enums === String ? $root.fluent_audio.v1.NodeState[message.state] === undefined ? message.state : $root.fluent_audio.v1.NodeState[message.state] : message.state;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.observedTimeNs != null && Object.hasOwnProperty.call(message, "observedTimeNs"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.observedTimeNs = typeof message.observedTimeNs === "number" ? BigInt(message.observedTimeNs) : $util.Long.fromBits(message.observedTimeNs.low >>> 0, message.observedTimeNs.high >>> 0, true).toBigInt();
                    else if (typeof message.observedTimeNs === "number")
                        object.observedTimeNs = options.longs === String ? String(message.observedTimeNs) : message.observedTimeNs;
                    else
                        object.observedTimeNs = options.longs === String ? $util.Long.prototype.toString.call(message.observedTimeNs) : options.longs === Number ? new $util.LongBits(message.observedTimeNs.low >>> 0, message.observedTimeNs.high >>> 0).toNumber(true) : message.observedTimeNs;
                if (message.message != null && Object.hasOwnProperty.call(message, "message")) {
                    object.message = message.message;
                    if (options.oneofs)
                        object._message = "message";
                }
                return object;
            };

            /**
             * Converts this NodeStatus to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.NodeStatus
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            NodeStatus.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for NodeStatus
             * @function getTypeUrl
             * @memberof fluent_audio.v1.NodeStatus
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            NodeStatus.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.NodeStatus";
            };

            return NodeStatus;
        })();

        v1.DiagnosticEvent = (function() {

            /**
             * Properties of a DiagnosticEvent.
             * @memberof fluent_audio.v1
             * @interface IDiagnosticEvent
             * @property {string|null} [nodeId] DiagnosticEvent nodeId
             * @property {fluent_audio.v1.DiagnosticSeverity|null} [severity] DiagnosticEvent severity
             * @property {number|Long|null} [seq] DiagnosticEvent seq
             * @property {number|Long|null} [observedTimeNs] DiagnosticEvent observedTimeNs
             * @property {string|null} [code] DiagnosticEvent code
             * @property {string|null} [message] DiagnosticEvent message
             */

            /**
             * Constructs a new DiagnosticEvent.
             * @memberof fluent_audio.v1
             * @classdesc Represents a DiagnosticEvent.
             * @implements IDiagnosticEvent
             * @constructor
             * @param {fluent_audio.v1.IDiagnosticEvent=} [properties] Properties to set
             */
            function DiagnosticEvent(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * DiagnosticEvent nodeId.
             * @member {string} nodeId
             * @memberof fluent_audio.v1.DiagnosticEvent
             * @instance
             */
            DiagnosticEvent.prototype.nodeId = "";

            /**
             * DiagnosticEvent severity.
             * @member {fluent_audio.v1.DiagnosticSeverity} severity
             * @memberof fluent_audio.v1.DiagnosticEvent
             * @instance
             */
            DiagnosticEvent.prototype.severity = 0;

            /**
             * DiagnosticEvent seq.
             * @member {number|Long} seq
             * @memberof fluent_audio.v1.DiagnosticEvent
             * @instance
             */
            DiagnosticEvent.prototype.seq = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * DiagnosticEvent observedTimeNs.
             * @member {number|Long} observedTimeNs
             * @memberof fluent_audio.v1.DiagnosticEvent
             * @instance
             */
            DiagnosticEvent.prototype.observedTimeNs = $util.Long ? $util.Long.fromBits(0,0,true) : 0;

            /**
             * DiagnosticEvent code.
             * @member {string} code
             * @memberof fluent_audio.v1.DiagnosticEvent
             * @instance
             */
            DiagnosticEvent.prototype.code = "";

            /**
             * DiagnosticEvent message.
             * @member {string} message
             * @memberof fluent_audio.v1.DiagnosticEvent
             * @instance
             */
            DiagnosticEvent.prototype.message = "";

            /**
             * Creates a new DiagnosticEvent instance using the specified properties.
             * @function create
             * @memberof fluent_audio.v1.DiagnosticEvent
             * @static
             * @param {fluent_audio.v1.IDiagnosticEvent=} [properties] Properties to set
             * @returns {fluent_audio.v1.DiagnosticEvent} DiagnosticEvent instance
             */
            DiagnosticEvent.create = function create(properties) {
                return new DiagnosticEvent(properties);
            };

            /**
             * Encodes the specified DiagnosticEvent message. Does not implicitly {@link fluent_audio.v1.DiagnosticEvent.verify|verify} messages.
             * @function encode
             * @memberof fluent_audio.v1.DiagnosticEvent
             * @static
             * @param {fluent_audio.v1.IDiagnosticEvent} message DiagnosticEvent message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            DiagnosticEvent.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.nodeId != null && Object.hasOwnProperty.call(message, "nodeId"))
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.nodeId);
                if (message.severity != null && Object.hasOwnProperty.call(message, "severity"))
                    writer.uint32(/* id 2, wireType 0 =*/16).int32(message.severity);
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    writer.uint32(/* id 3, wireType 0 =*/24).uint64(message.seq);
                if (message.observedTimeNs != null && Object.hasOwnProperty.call(message, "observedTimeNs"))
                    writer.uint32(/* id 4, wireType 0 =*/32).uint64(message.observedTimeNs);
                if (message.code != null && Object.hasOwnProperty.call(message, "code"))
                    writer.uint32(/* id 5, wireType 2 =*/42).string(message.code);
                if (message.message != null && Object.hasOwnProperty.call(message, "message"))
                    writer.uint32(/* id 6, wireType 2 =*/50).string(message.message);
                return writer;
            };

            /**
             * Encodes the specified DiagnosticEvent message, length delimited. Does not implicitly {@link fluent_audio.v1.DiagnosticEvent.verify|verify} messages.
             * @function encodeDelimited
             * @memberof fluent_audio.v1.DiagnosticEvent
             * @static
             * @param {fluent_audio.v1.IDiagnosticEvent} message DiagnosticEvent message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            DiagnosticEvent.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes a DiagnosticEvent message from the specified reader or buffer.
             * @function decode
             * @memberof fluent_audio.v1.DiagnosticEvent
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {fluent_audio.v1.DiagnosticEvent} DiagnosticEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            DiagnosticEvent.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.fluent_audio.v1.DiagnosticEvent();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.nodeId = reader.string();
                            break;
                        }
                    case 2: {
                            message.severity = reader.int32();
                            break;
                        }
                    case 3: {
                            message.seq = reader.uint64();
                            break;
                        }
                    case 4: {
                            message.observedTimeNs = reader.uint64();
                            break;
                        }
                    case 5: {
                            message.code = reader.string();
                            break;
                        }
                    case 6: {
                            message.message = reader.string();
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes a DiagnosticEvent message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof fluent_audio.v1.DiagnosticEvent
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {fluent_audio.v1.DiagnosticEvent} DiagnosticEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            DiagnosticEvent.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a DiagnosticEvent message.
             * @function verify
             * @memberof fluent_audio.v1.DiagnosticEvent
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            DiagnosticEvent.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.nodeId != null && Object.hasOwnProperty.call(message, "nodeId"))
                    if (!$util.isString(message.nodeId))
                        return "nodeId: string expected";
                if (message.severity != null && Object.hasOwnProperty.call(message, "severity"))
                    switch (message.severity) {
                    default:
                        return "severity: enum value expected";
                    case 0:
                    case 1:
                    case 2:
                    case 3:
                    case 4:
                        break;
                    }
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (!$util.isInteger(message.seq) && !(message.seq && $util.isInteger(message.seq.low) && $util.isInteger(message.seq.high)))
                        return "seq: integer|Long expected";
                if (message.observedTimeNs != null && Object.hasOwnProperty.call(message, "observedTimeNs"))
                    if (!$util.isInteger(message.observedTimeNs) && !(message.observedTimeNs && $util.isInteger(message.observedTimeNs.low) && $util.isInteger(message.observedTimeNs.high)))
                        return "observedTimeNs: integer|Long expected";
                if (message.code != null && Object.hasOwnProperty.call(message, "code"))
                    if (!$util.isString(message.code))
                        return "code: string expected";
                if (message.message != null && Object.hasOwnProperty.call(message, "message"))
                    if (!$util.isString(message.message))
                        return "message: string expected";
                return null;
            };

            /**
             * Creates a DiagnosticEvent message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof fluent_audio.v1.DiagnosticEvent
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {fluent_audio.v1.DiagnosticEvent} DiagnosticEvent
             */
            DiagnosticEvent.fromObject = function fromObject(object, long) {
                if (object instanceof $root.fluent_audio.v1.DiagnosticEvent)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".fluent_audio.v1.DiagnosticEvent: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.fluent_audio.v1.DiagnosticEvent();
                if (object.nodeId != null)
                    message.nodeId = String(object.nodeId);
                switch (object.severity) {
                default:
                    if (typeof object.severity === "number") {
                        message.severity = object.severity;
                        break;
                    }
                    break;
                case "DIAGNOSTIC_SEVERITY_UNSPECIFIED":
                case 0:
                    message.severity = 0;
                    break;
                case "DIAGNOSTIC_SEVERITY_OK":
                case 1:
                    message.severity = 1;
                    break;
                case "DIAGNOSTIC_SEVERITY_WARN":
                case 2:
                    message.severity = 2;
                    break;
                case "DIAGNOSTIC_SEVERITY_ERROR":
                case 3:
                    message.severity = 3;
                    break;
                case "DIAGNOSTIC_SEVERITY_FATAL":
                case 4:
                    message.severity = 4;
                    break;
                }
                if (object.seq != null)
                    if ($util.Long)
                        message.seq = $util.Long.fromValue(object.seq, true);
                    else if (typeof object.seq === "string")
                        message.seq = parseInt(object.seq, 10);
                    else if (typeof object.seq === "number")
                        message.seq = object.seq;
                    else if (typeof object.seq === "object")
                        message.seq = new $util.LongBits(object.seq.low >>> 0, object.seq.high >>> 0).toNumber(true);
                if (object.observedTimeNs != null)
                    if ($util.Long)
                        message.observedTimeNs = $util.Long.fromValue(object.observedTimeNs, true);
                    else if (typeof object.observedTimeNs === "string")
                        message.observedTimeNs = parseInt(object.observedTimeNs, 10);
                    else if (typeof object.observedTimeNs === "number")
                        message.observedTimeNs = object.observedTimeNs;
                    else if (typeof object.observedTimeNs === "object")
                        message.observedTimeNs = new $util.LongBits(object.observedTimeNs.low >>> 0, object.observedTimeNs.high >>> 0).toNumber(true);
                if (object.code != null)
                    message.code = String(object.code);
                if (object.message != null)
                    message.message = String(object.message);
                return message;
            };

            /**
             * Creates a plain object from a DiagnosticEvent message. Also converts values to other types if specified.
             * @function toObject
             * @memberof fluent_audio.v1.DiagnosticEvent
             * @static
             * @param {fluent_audio.v1.DiagnosticEvent} message DiagnosticEvent
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            DiagnosticEvent.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.defaults) {
                    object.nodeId = "";
                    object.severity = options.enums === String ? "DIAGNOSTIC_SEVERITY_UNSPECIFIED" : 0;
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.seq = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.seq = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    if ($util.Long) {
                        var long = new $util.Long(0, 0, true);
                        object.observedTimeNs = options.longs === String ? long.toString() : options.longs === Number ? long.toNumber() : typeof BigInt !== "undefined" && options.longs === BigInt ? long.toBigInt() : long;
                    } else
                        object.observedTimeNs = options.longs === String ? "0" : typeof BigInt !== "undefined" && options.longs === BigInt ? BigInt("0") : 0;
                    object.code = "";
                    object.message = "";
                }
                if (message.nodeId != null && Object.hasOwnProperty.call(message, "nodeId"))
                    object.nodeId = message.nodeId;
                if (message.severity != null && Object.hasOwnProperty.call(message, "severity"))
                    object.severity = options.enums === String ? $root.fluent_audio.v1.DiagnosticSeverity[message.severity] === undefined ? message.severity : $root.fluent_audio.v1.DiagnosticSeverity[message.severity] : message.severity;
                if (message.seq != null && Object.hasOwnProperty.call(message, "seq"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.seq = typeof message.seq === "number" ? BigInt(message.seq) : $util.Long.fromBits(message.seq.low >>> 0, message.seq.high >>> 0, true).toBigInt();
                    else if (typeof message.seq === "number")
                        object.seq = options.longs === String ? String(message.seq) : message.seq;
                    else
                        object.seq = options.longs === String ? $util.Long.prototype.toString.call(message.seq) : options.longs === Number ? new $util.LongBits(message.seq.low >>> 0, message.seq.high >>> 0).toNumber(true) : message.seq;
                if (message.observedTimeNs != null && Object.hasOwnProperty.call(message, "observedTimeNs"))
                    if (typeof BigInt !== "undefined" && options.longs === BigInt)
                        object.observedTimeNs = typeof message.observedTimeNs === "number" ? BigInt(message.observedTimeNs) : $util.Long.fromBits(message.observedTimeNs.low >>> 0, message.observedTimeNs.high >>> 0, true).toBigInt();
                    else if (typeof message.observedTimeNs === "number")
                        object.observedTimeNs = options.longs === String ? String(message.observedTimeNs) : message.observedTimeNs;
                    else
                        object.observedTimeNs = options.longs === String ? $util.Long.prototype.toString.call(message.observedTimeNs) : options.longs === Number ? new $util.LongBits(message.observedTimeNs.low >>> 0, message.observedTimeNs.high >>> 0).toNumber(true) : message.observedTimeNs;
                if (message.code != null && Object.hasOwnProperty.call(message, "code"))
                    object.code = message.code;
                if (message.message != null && Object.hasOwnProperty.call(message, "message"))
                    object.message = message.message;
                return object;
            };

            /**
             * Converts this DiagnosticEvent to JSON.
             * @function toJSON
             * @memberof fluent_audio.v1.DiagnosticEvent
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            DiagnosticEvent.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for DiagnosticEvent
             * @function getTypeUrl
             * @memberof fluent_audio.v1.DiagnosticEvent
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            DiagnosticEvent.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/fluent_audio.v1.DiagnosticEvent";
            };

            return DiagnosticEvent;
        })();

        return v1;
    })();

    return fluent_audio;
})();

$root.google = (function() {

    /**
     * Namespace google.
     * @exports google
     * @namespace
     */
    var google = {};

    google.protobuf = (function() {

        /**
         * Namespace protobuf.
         * @memberof google
         * @namespace
         */
        var protobuf = {};

        protobuf.Struct = (function() {

            /**
             * Properties of a Struct.
             * @memberof google.protobuf
             * @interface IStruct
             * @property {Object.<string,google.protobuf.IValue>|null} [fields] Struct fields
             */

            /**
             * Constructs a new Struct.
             * @memberof google.protobuf
             * @classdesc Represents a Struct.
             * @implements IStruct
             * @constructor
             * @param {google.protobuf.IStruct=} [properties] Properties to set
             */
            function Struct(properties) {
                this.fields = {};
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * Struct fields.
             * @member {Object.<string,google.protobuf.IValue>} fields
             * @memberof google.protobuf.Struct
             * @instance
             */
            Struct.prototype.fields = $util.emptyObject;

            /**
             * Creates a new Struct instance using the specified properties.
             * @function create
             * @memberof google.protobuf.Struct
             * @static
             * @param {google.protobuf.IStruct=} [properties] Properties to set
             * @returns {google.protobuf.Struct} Struct instance
             */
            Struct.create = function create(properties) {
                return new Struct(properties);
            };

            /**
             * Encodes the specified Struct message. Does not implicitly {@link google.protobuf.Struct.verify|verify} messages.
             * @function encode
             * @memberof google.protobuf.Struct
             * @static
             * @param {google.protobuf.IStruct} message Struct message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            Struct.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.fields != null && Object.hasOwnProperty.call(message, "fields"))
                    for (var keys = Object.keys(message.fields), i = 0; i < keys.length; ++i) {
                        writer.uint32(/* id 1, wireType 2 =*/10).fork().uint32(/* id 1, wireType 2 =*/10).string(keys[i]);
                        $root.google.protobuf.Value.encode(message.fields[keys[i]], writer.uint32(/* id 2, wireType 2 =*/18).fork(), q + 1).ldelim().ldelim();
                    }
                return writer;
            };

            /**
             * Encodes the specified Struct message, length delimited. Does not implicitly {@link google.protobuf.Struct.verify|verify} messages.
             * @function encodeDelimited
             * @memberof google.protobuf.Struct
             * @static
             * @param {google.protobuf.IStruct} message Struct message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            Struct.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes a Struct message from the specified reader or buffer.
             * @function decode
             * @memberof google.protobuf.Struct
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {google.protobuf.Struct} Struct
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            Struct.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.google.protobuf.Struct(), key, value;
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            if (message.fields === $util.emptyObject)
                                message.fields = {};
                            var end2 = reader.uint32() + reader.pos;
                            key = "";
                            value = null;
                            while (reader.pos < end2) {
                                var tag2 = reader.uint32();
                                switch (tag2 >>> 3) {
                                case 1:
                                    key = reader.string();
                                    break;
                                case 2:
                                    value = $root.google.protobuf.Value.decode(reader, reader.uint32(), undefined, long + 1);
                                    break;
                                default:
                                    reader.skipType(tag2 & 7, long);
                                    break;
                                }
                            }
                            if (key === "__proto__")
                                $util.makeProp(message.fields, key);
                            message.fields[key] = value;
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes a Struct message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof google.protobuf.Struct
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {google.protobuf.Struct} Struct
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            Struct.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a Struct message.
             * @function verify
             * @memberof google.protobuf.Struct
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            Struct.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.fields != null && Object.hasOwnProperty.call(message, "fields")) {
                    if (!$util.isObject(message.fields))
                        return "fields: object expected";
                    var key = Object.keys(message.fields);
                    for (var i = 0; i < key.length; ++i) {
                        var error = $root.google.protobuf.Value.verify(message.fields[key[i]], long + 1);
                        if (error)
                            return "fields." + error;
                    }
                }
                return null;
            };

            /**
             * Creates a Struct message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof google.protobuf.Struct
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {google.protobuf.Struct} Struct
             */
            Struct.fromObject = function fromObject(object, long) {
                if (object instanceof $root.google.protobuf.Struct)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".google.protobuf.Struct: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.google.protobuf.Struct();
                if (object.fields) {
                    if (!$util.isObject(object.fields))
                        throw TypeError(".google.protobuf.Struct.fields: object expected");
                    message.fields = {};
                    for (var keys = Object.keys(object.fields), i = 0; i < keys.length; ++i) {
                        if (keys[i] === "__proto__")
                            $util.makeProp(message.fields, keys[i]);
                        if (!$util.isObject(object.fields[keys[i]]))
                            throw TypeError(".google.protobuf.Struct.fields: object expected");
                        message.fields[keys[i]] = $root.google.protobuf.Value.fromObject(object.fields[keys[i]], long + 1);
                    }
                }
                return message;
            };

            /**
             * Creates a plain object from a Struct message. Also converts values to other types if specified.
             * @function toObject
             * @memberof google.protobuf.Struct
             * @static
             * @param {google.protobuf.Struct} message Struct
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            Struct.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.objects || options.defaults)
                    object.fields = {};
                var keys2;
                if (message.fields && (keys2 = Object.keys(message.fields)).length) {
                    object.fields = {};
                    for (var j = 0; j < keys2.length; ++j) {
                        if (keys2[j] === "__proto__")
                            $util.makeProp(object.fields, keys2[j]);
                        object.fields[keys2[j]] = $root.google.protobuf.Value.toObject(message.fields[keys2[j]], options, q + 1);
                    }
                }
                return object;
            };

            /**
             * Converts this Struct to JSON.
             * @function toJSON
             * @memberof google.protobuf.Struct
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            Struct.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for Struct
             * @function getTypeUrl
             * @memberof google.protobuf.Struct
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            Struct.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/google.protobuf.Struct";
            };

            return Struct;
        })();

        protobuf.Value = (function() {

            /**
             * Properties of a Value.
             * @memberof google.protobuf
             * @interface IValue
             * @property {google.protobuf.NullValue|null} [nullValue] Value nullValue
             * @property {number|null} [numberValue] Value numberValue
             * @property {string|null} [stringValue] Value stringValue
             * @property {boolean|null} [boolValue] Value boolValue
             * @property {google.protobuf.IStruct|null} [structValue] Value structValue
             * @property {google.protobuf.IListValue|null} [listValue] Value listValue
             */

            /**
             * Constructs a new Value.
             * @memberof google.protobuf
             * @classdesc Represents a Value.
             * @implements IValue
             * @constructor
             * @param {google.protobuf.IValue=} [properties] Properties to set
             */
            function Value(properties) {
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * Value nullValue.
             * @member {google.protobuf.NullValue|null|undefined} nullValue
             * @memberof google.protobuf.Value
             * @instance
             */
            Value.prototype.nullValue = null;

            /**
             * Value numberValue.
             * @member {number|null|undefined} numberValue
             * @memberof google.protobuf.Value
             * @instance
             */
            Value.prototype.numberValue = null;

            /**
             * Value stringValue.
             * @member {string|null|undefined} stringValue
             * @memberof google.protobuf.Value
             * @instance
             */
            Value.prototype.stringValue = null;

            /**
             * Value boolValue.
             * @member {boolean|null|undefined} boolValue
             * @memberof google.protobuf.Value
             * @instance
             */
            Value.prototype.boolValue = null;

            /**
             * Value structValue.
             * @member {google.protobuf.IStruct|null|undefined} structValue
             * @memberof google.protobuf.Value
             * @instance
             */
            Value.prototype.structValue = null;

            /**
             * Value listValue.
             * @member {google.protobuf.IListValue|null|undefined} listValue
             * @memberof google.protobuf.Value
             * @instance
             */
            Value.prototype.listValue = null;

            // OneOf field names bound to virtual getters and setters
            var $oneOfFields;

            /**
             * Value kind.
             * @member {"nullValue"|"numberValue"|"stringValue"|"boolValue"|"structValue"|"listValue"|undefined} kind
             * @memberof google.protobuf.Value
             * @instance
             */
            Object.defineProperty(Value.prototype, "kind", {
                get: $util.oneOfGetter($oneOfFields = ["nullValue", "numberValue", "stringValue", "boolValue", "structValue", "listValue"]),
                set: $util.oneOfSetter($oneOfFields)
            });

            /**
             * Creates a new Value instance using the specified properties.
             * @function create
             * @memberof google.protobuf.Value
             * @static
             * @param {google.protobuf.IValue=} [properties] Properties to set
             * @returns {google.protobuf.Value} Value instance
             */
            Value.create = function create(properties) {
                return new Value(properties);
            };

            /**
             * Encodes the specified Value message. Does not implicitly {@link google.protobuf.Value.verify|verify} messages.
             * @function encode
             * @memberof google.protobuf.Value
             * @static
             * @param {google.protobuf.IValue} message Value message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            Value.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.nullValue != null && Object.hasOwnProperty.call(message, "nullValue"))
                    writer.uint32(/* id 1, wireType 0 =*/8).int32(message.nullValue);
                if (message.numberValue != null && Object.hasOwnProperty.call(message, "numberValue"))
                    writer.uint32(/* id 2, wireType 1 =*/17).double(message.numberValue);
                if (message.stringValue != null && Object.hasOwnProperty.call(message, "stringValue"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.stringValue);
                if (message.boolValue != null && Object.hasOwnProperty.call(message, "boolValue"))
                    writer.uint32(/* id 4, wireType 0 =*/32).bool(message.boolValue);
                if (message.structValue != null && Object.hasOwnProperty.call(message, "structValue"))
                    $root.google.protobuf.Struct.encode(message.structValue, writer.uint32(/* id 5, wireType 2 =*/42).fork(), q + 1).ldelim();
                if (message.listValue != null && Object.hasOwnProperty.call(message, "listValue"))
                    $root.google.protobuf.ListValue.encode(message.listValue, writer.uint32(/* id 6, wireType 2 =*/50).fork(), q + 1).ldelim();
                return writer;
            };

            /**
             * Encodes the specified Value message, length delimited. Does not implicitly {@link google.protobuf.Value.verify|verify} messages.
             * @function encodeDelimited
             * @memberof google.protobuf.Value
             * @static
             * @param {google.protobuf.IValue} message Value message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            Value.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes a Value message from the specified reader or buffer.
             * @function decode
             * @memberof google.protobuf.Value
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {google.protobuf.Value} Value
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            Value.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.google.protobuf.Value();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            message.nullValue = reader.int32();
                            break;
                        }
                    case 2: {
                            message.numberValue = reader.double();
                            break;
                        }
                    case 3: {
                            message.stringValue = reader.string();
                            break;
                        }
                    case 4: {
                            message.boolValue = reader.bool();
                            break;
                        }
                    case 5: {
                            message.structValue = $root.google.protobuf.Struct.decode(reader, reader.uint32(), undefined, long + 1);
                            break;
                        }
                    case 6: {
                            message.listValue = $root.google.protobuf.ListValue.decode(reader, reader.uint32(), undefined, long + 1);
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes a Value message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof google.protobuf.Value
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {google.protobuf.Value} Value
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            Value.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a Value message.
             * @function verify
             * @memberof google.protobuf.Value
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            Value.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                var properties = {};
                if (message.nullValue != null && Object.hasOwnProperty.call(message, "nullValue")) {
                    properties.kind = 1;
                    switch (message.nullValue) {
                    default:
                        return "nullValue: enum value expected";
                    case 0:
                        break;
                    }
                }
                if (message.numberValue != null && Object.hasOwnProperty.call(message, "numberValue")) {
                    if (properties.kind === 1)
                        return "kind: multiple values";
                    properties.kind = 1;
                    if (typeof message.numberValue !== "number")
                        return "numberValue: number expected";
                }
                if (message.stringValue != null && Object.hasOwnProperty.call(message, "stringValue")) {
                    if (properties.kind === 1)
                        return "kind: multiple values";
                    properties.kind = 1;
                    if (!$util.isString(message.stringValue))
                        return "stringValue: string expected";
                }
                if (message.boolValue != null && Object.hasOwnProperty.call(message, "boolValue")) {
                    if (properties.kind === 1)
                        return "kind: multiple values";
                    properties.kind = 1;
                    if (typeof message.boolValue !== "boolean")
                        return "boolValue: boolean expected";
                }
                if (message.structValue != null && Object.hasOwnProperty.call(message, "structValue")) {
                    if (properties.kind === 1)
                        return "kind: multiple values";
                    properties.kind = 1;
                    {
                        var error = $root.google.protobuf.Struct.verify(message.structValue, long + 1);
                        if (error)
                            return "structValue." + error;
                    }
                }
                if (message.listValue != null && Object.hasOwnProperty.call(message, "listValue")) {
                    if (properties.kind === 1)
                        return "kind: multiple values";
                    properties.kind = 1;
                    {
                        var error = $root.google.protobuf.ListValue.verify(message.listValue, long + 1);
                        if (error)
                            return "listValue." + error;
                    }
                }
                return null;
            };

            /**
             * Creates a Value message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof google.protobuf.Value
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {google.protobuf.Value} Value
             */
            Value.fromObject = function fromObject(object, long) {
                if (object instanceof $root.google.protobuf.Value)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".google.protobuf.Value: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.google.protobuf.Value();
                switch (object.nullValue) {
                default:
                    if (typeof object.nullValue === "number") {
                        message.nullValue = object.nullValue;
                        break;
                    }
                    break;
                case "NULL_VALUE":
                case 0:
                    message.nullValue = 0;
                    break;
                }
                if (object.numberValue != null)
                    message.numberValue = Number(object.numberValue);
                if (object.stringValue != null)
                    message.stringValue = String(object.stringValue);
                if (object.boolValue != null)
                    message.boolValue = Boolean(object.boolValue);
                if (object.structValue != null) {
                    if (!$util.isObject(object.structValue))
                        throw TypeError(".google.protobuf.Value.structValue: object expected");
                    message.structValue = $root.google.protobuf.Struct.fromObject(object.structValue, long + 1);
                }
                if (object.listValue != null) {
                    if (!$util.isObject(object.listValue))
                        throw TypeError(".google.protobuf.Value.listValue: object expected");
                    message.listValue = $root.google.protobuf.ListValue.fromObject(object.listValue, long + 1);
                }
                return message;
            };

            /**
             * Creates a plain object from a Value message. Also converts values to other types if specified.
             * @function toObject
             * @memberof google.protobuf.Value
             * @static
             * @param {google.protobuf.Value} message Value
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            Value.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (message.nullValue != null && Object.hasOwnProperty.call(message, "nullValue")) {
                    object.nullValue = options.enums === String ? $root.google.protobuf.NullValue[message.nullValue] === undefined ? message.nullValue : $root.google.protobuf.NullValue[message.nullValue] : message.nullValue;
                    if (options.oneofs)
                        object.kind = "nullValue";
                }
                if (message.numberValue != null && Object.hasOwnProperty.call(message, "numberValue")) {
                    object.numberValue = options.json && !isFinite(message.numberValue) ? String(message.numberValue) : message.numberValue;
                    if (options.oneofs)
                        object.kind = "numberValue";
                }
                if (message.stringValue != null && Object.hasOwnProperty.call(message, "stringValue")) {
                    object.stringValue = message.stringValue;
                    if (options.oneofs)
                        object.kind = "stringValue";
                }
                if (message.boolValue != null && Object.hasOwnProperty.call(message, "boolValue")) {
                    object.boolValue = message.boolValue;
                    if (options.oneofs)
                        object.kind = "boolValue";
                }
                if (message.structValue != null && Object.hasOwnProperty.call(message, "structValue")) {
                    object.structValue = $root.google.protobuf.Struct.toObject(message.structValue, options, q + 1);
                    if (options.oneofs)
                        object.kind = "structValue";
                }
                if (message.listValue != null && Object.hasOwnProperty.call(message, "listValue")) {
                    object.listValue = $root.google.protobuf.ListValue.toObject(message.listValue, options, q + 1);
                    if (options.oneofs)
                        object.kind = "listValue";
                }
                return object;
            };

            /**
             * Converts this Value to JSON.
             * @function toJSON
             * @memberof google.protobuf.Value
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            Value.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for Value
             * @function getTypeUrl
             * @memberof google.protobuf.Value
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            Value.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/google.protobuf.Value";
            };

            return Value;
        })();

        /**
         * NullValue enum.
         * @name google.protobuf.NullValue
         * @enum {number}
         * @property {number} NULL_VALUE=0 NULL_VALUE value
         */
        protobuf.NullValue = (function() {
            var valuesById = {}, values = Object.create(valuesById);
            values[valuesById[0] = "NULL_VALUE"] = 0;
            return values;
        })();

        protobuf.ListValue = (function() {

            /**
             * Properties of a ListValue.
             * @memberof google.protobuf
             * @interface IListValue
             * @property {Array.<google.protobuf.IValue>|null} [values] ListValue values
             */

            /**
             * Constructs a new ListValue.
             * @memberof google.protobuf
             * @classdesc Represents a ListValue.
             * @implements IListValue
             * @constructor
             * @param {google.protobuf.IListValue=} [properties] Properties to set
             */
            function ListValue(properties) {
                this.values = [];
                if (properties)
                    for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            }

            /**
             * ListValue values.
             * @member {Array.<google.protobuf.IValue>} values
             * @memberof google.protobuf.ListValue
             * @instance
             */
            ListValue.prototype.values = $util.emptyArray;

            /**
             * Creates a new ListValue instance using the specified properties.
             * @function create
             * @memberof google.protobuf.ListValue
             * @static
             * @param {google.protobuf.IListValue=} [properties] Properties to set
             * @returns {google.protobuf.ListValue} ListValue instance
             */
            ListValue.create = function create(properties) {
                return new ListValue(properties);
            };

            /**
             * Encodes the specified ListValue message. Does not implicitly {@link google.protobuf.ListValue.verify|verify} messages.
             * @function encode
             * @memberof google.protobuf.ListValue
             * @static
             * @param {google.protobuf.IListValue} message ListValue message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            ListValue.encode = function encode(message, writer, q) {
                if (!writer)
                    writer = $Writer.create();
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                if (message.values != null && message.values.length)
                    for (var i = 0; i < message.values.length; ++i)
                        $root.google.protobuf.Value.encode(message.values[i], writer.uint32(/* id 1, wireType 2 =*/10).fork(), q + 1).ldelim();
                return writer;
            };

            /**
             * Encodes the specified ListValue message, length delimited. Does not implicitly {@link google.protobuf.ListValue.verify|verify} messages.
             * @function encodeDelimited
             * @memberof google.protobuf.ListValue
             * @static
             * @param {google.protobuf.IListValue} message ListValue message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            ListValue.encodeDelimited = function encodeDelimited(message, writer) {
                return this.encode(message, writer && writer.len ? writer.fork() : writer).ldelim();
            };

            /**
             * Decodes a ListValue message from the specified reader or buffer.
             * @function decode
             * @memberof google.protobuf.ListValue
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {google.protobuf.ListValue} ListValue
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            ListValue.decode = function decode(reader, length, error, long) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (long === undefined)
                    long = 0;
                if (long > $Reader.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var end = length === undefined ? reader.len : reader.pos + length, message = new $root.google.protobuf.ListValue();
                while (reader.pos < end) {
                    var tag = reader.uint32();
                    if (tag === error)
                        break;
                    switch (tag >>> 3) {
                    case 1: {
                            if (!(message.values && message.values.length))
                                message.values = [];
                            message.values.push($root.google.protobuf.Value.decode(reader, reader.uint32(), undefined, long + 1));
                            break;
                        }
                    default:
                        reader.skipType(tag & 7, long);
                        break;
                    }
                }
                return message;
            };

            /**
             * Decodes a ListValue message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof google.protobuf.ListValue
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {google.protobuf.ListValue} ListValue
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            ListValue.decodeDelimited = function decodeDelimited(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a ListValue message.
             * @function verify
             * @memberof google.protobuf.ListValue
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            ListValue.verify = function verify(message, long) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    return "maximum nesting depth exceeded";
                if (message.values != null && Object.hasOwnProperty.call(message, "values")) {
                    if (!Array.isArray(message.values))
                        return "values: array expected";
                    for (var i = 0; i < message.values.length; ++i) {
                        var error = $root.google.protobuf.Value.verify(message.values[i], long + 1);
                        if (error)
                            return "values." + error;
                    }
                }
                return null;
            };

            /**
             * Creates a ListValue message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof google.protobuf.ListValue
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {google.protobuf.ListValue} ListValue
             */
            ListValue.fromObject = function fromObject(object, long) {
                if (object instanceof $root.google.protobuf.ListValue)
                    return object;
                if (!$util.isObject(object))
                    throw TypeError(".google.protobuf.ListValue: object expected");
                if (long === undefined)
                    long = 0;
                if (long > $util.recursionLimit)
                    throw Error("maximum nesting depth exceeded");
                var message = new $root.google.protobuf.ListValue();
                if (object.values) {
                    if (!Array.isArray(object.values))
                        throw TypeError(".google.protobuf.ListValue.values: array expected");
                    message.values = [];
                    for (var i = 0; i < object.values.length; ++i) {
                        if (!$util.isObject(object.values[i]))
                            throw TypeError(".google.protobuf.ListValue.values: object expected");
                        message.values[i] = $root.google.protobuf.Value.fromObject(object.values[i], long + 1);
                    }
                }
                return message;
            };

            /**
             * Creates a plain object from a ListValue message. Also converts values to other types if specified.
             * @function toObject
             * @memberof google.protobuf.ListValue
             * @static
             * @param {google.protobuf.ListValue} message ListValue
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            ListValue.toObject = function toObject(message, options, q) {
                if (!options)
                    options = {};
                if (q === undefined)
                    q = 0;
                if (q > $util.recursionLimit)
                    throw Error("max depth exceeded");
                var object = {};
                if (options.arrays || options.defaults)
                    object.values = [];
                if (message.values && message.values.length) {
                    object.values = [];
                    for (var j = 0; j < message.values.length; ++j)
                        object.values[j] = $root.google.protobuf.Value.toObject(message.values[j], options, q + 1);
                }
                return object;
            };

            /**
             * Converts this ListValue to JSON.
             * @function toJSON
             * @memberof google.protobuf.ListValue
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            ListValue.prototype.toJSON = function toJSON() {
                return this.constructor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the default type url for ListValue
             * @function getTypeUrl
             * @memberof google.protobuf.ListValue
             * @static
             * @param {string} [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns {string} The default type url
             */
            ListValue.getTypeUrl = function getTypeUrl(typeUrlPrefix) {
                if (typeUrlPrefix === undefined) {
                    typeUrlPrefix = "type.googleapis.com";
                }
                return typeUrlPrefix + "/google.protobuf.ListValue";
            };

            return ListValue;
        })();

        return protobuf;
    })();

    return google;
})();

module.exports = $root;
