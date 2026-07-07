import * as $protobuf from "protobufjs";
import Long = require("long");
/** Namespace fluent_dialogue_dora. */
export namespace fluent_dialogue_dora {

    /** Namespace v1. */
    namespace v1 {

        /** SampleFormat enum. */
        enum SampleFormat {
            SAMPLE_FORMAT_UNSPECIFIED = 0,
            SAMPLE_FORMAT_S16LE = 1,
            SAMPLE_FORMAT_F32LE = 2
        }

        /** ChannelLayout enum. */
        enum ChannelLayout {
            CHANNEL_LAYOUT_UNSPECIFIED = 0,
            CHANNEL_LAYOUT_INTERLEAVED = 1
        }

        /** Properties of an AudioFormat. */
        interface IAudioFormat {

            /** AudioFormat sampleRateHz */
            sampleRateHz?: (number|null);

            /** AudioFormat channels */
            channels?: (number|null);

            /** AudioFormat sampleFormat */
            sampleFormat?: (fluent_dialogue_dora.v1.SampleFormat|null);

            /** AudioFormat channelLayout */
            channelLayout?: (fluent_dialogue_dora.v1.ChannelLayout|null);
        }

        /** Represents an AudioFormat. */
        class AudioFormat implements IAudioFormat {

            /**
             * Constructs a new AudioFormat.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IAudioFormat);

            /** AudioFormat sampleRateHz. */
            public sampleRateHz: number;

            /** AudioFormat channels. */
            public channels: number;

            /** AudioFormat sampleFormat. */
            public sampleFormat: fluent_dialogue_dora.v1.SampleFormat;

            /** AudioFormat channelLayout. */
            public channelLayout: fluent_dialogue_dora.v1.ChannelLayout;

            /**
             * Creates a new AudioFormat instance using the specified properties.
             * @param [properties] Properties to set
             * @returns AudioFormat instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IAudioFormat): fluent_dialogue_dora.v1.AudioFormat;

            /**
             * Encodes the specified AudioFormat message. Does not implicitly {@link fluent_dialogue_dora.v1.AudioFormat.verify|verify} messages.
             * @param message AudioFormat message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IAudioFormat, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified AudioFormat message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.AudioFormat.verify|verify} messages.
             * @param message AudioFormat message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IAudioFormat, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an AudioFormat message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns AudioFormat
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.AudioFormat;

            /**
             * Decodes an AudioFormat message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns AudioFormat
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.AudioFormat;

            /**
             * Verifies an AudioFormat message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates an AudioFormat message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns AudioFormat
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.AudioFormat;

            /**
             * Creates a plain object from an AudioFormat message. Also converts values to other types if specified.
             * @param message AudioFormat
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.AudioFormat, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this AudioFormat to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for AudioFormat
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an AudioFrame. */
        interface IAudioFrame {

            /** AudioFrame sourceId */
            sourceId?: (string|null);

            /** AudioFrame streamId */
            streamId?: (string|null);

            /** AudioFrame seq */
            seq?: (number|Long|null);

            /** AudioFrame sampleIndex */
            sampleIndex?: (number|Long|null);

            /** AudioFrame captureTimeNs */
            captureTimeNs?: (number|Long|null);

            /** AudioFrame frameCount */
            frameCount?: (number|null);

            /** AudioFrame format */
            format?: (fluent_dialogue_dora.v1.IAudioFormat|null);

            /** AudioFrame payload */
            payload?: (Uint8Array|null);
        }

        /** Represents an AudioFrame. */
        class AudioFrame implements IAudioFrame {

            /**
             * Constructs a new AudioFrame.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IAudioFrame);

            /** AudioFrame sourceId. */
            public sourceId: string;

            /** AudioFrame streamId. */
            public streamId: string;

            /** AudioFrame seq. */
            public seq: (number|Long);

            /** AudioFrame sampleIndex. */
            public sampleIndex: (number|Long);

            /** AudioFrame captureTimeNs. */
            public captureTimeNs: (number|Long);

            /** AudioFrame frameCount. */
            public frameCount: number;

            /** AudioFrame format. */
            public format?: (fluent_dialogue_dora.v1.IAudioFormat|null);

            /** AudioFrame payload. */
            public payload: Uint8Array;

            /**
             * Creates a new AudioFrame instance using the specified properties.
             * @param [properties] Properties to set
             * @returns AudioFrame instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IAudioFrame): fluent_dialogue_dora.v1.AudioFrame;

            /**
             * Encodes the specified AudioFrame message. Does not implicitly {@link fluent_dialogue_dora.v1.AudioFrame.verify|verify} messages.
             * @param message AudioFrame message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IAudioFrame, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified AudioFrame message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.AudioFrame.verify|verify} messages.
             * @param message AudioFrame message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IAudioFrame, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an AudioFrame message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns AudioFrame
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.AudioFrame;

            /**
             * Decodes an AudioFrame message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns AudioFrame
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.AudioFrame;

            /**
             * Verifies an AudioFrame message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates an AudioFrame message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns AudioFrame
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.AudioFrame;

            /**
             * Creates a plain object from an AudioFrame message. Also converts values to other types if specified.
             * @param message AudioFrame
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.AudioFrame, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this AudioFrame to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for AudioFrame
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an AudioStreamFinal. */
        interface IAudioStreamFinal {

            /** AudioStreamFinal sourceId */
            sourceId?: (string|null);

            /** AudioStreamFinal streamId */
            streamId?: (string|null);

            /** AudioStreamFinal seq */
            seq?: (number|Long|null);

            /** AudioStreamFinal sampleIndex */
            sampleIndex?: (number|Long|null);

            /** AudioStreamFinal captureTimeNs */
            captureTimeNs?: (number|Long|null);

            /** AudioStreamFinal format */
            format?: (fluent_dialogue_dora.v1.IAudioFormat|null);
        }

        /** Represents an AudioStreamFinal. */
        class AudioStreamFinal implements IAudioStreamFinal {

            /**
             * Constructs a new AudioStreamFinal.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IAudioStreamFinal);

            /** AudioStreamFinal sourceId. */
            public sourceId: string;

            /** AudioStreamFinal streamId. */
            public streamId: string;

            /** AudioStreamFinal seq. */
            public seq: (number|Long);

            /** AudioStreamFinal sampleIndex. */
            public sampleIndex: (number|Long);

            /** AudioStreamFinal captureTimeNs. */
            public captureTimeNs: (number|Long);

            /** AudioStreamFinal format. */
            public format?: (fluent_dialogue_dora.v1.IAudioFormat|null);

            /**
             * Creates a new AudioStreamFinal instance using the specified properties.
             * @param [properties] Properties to set
             * @returns AudioStreamFinal instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IAudioStreamFinal): fluent_dialogue_dora.v1.AudioStreamFinal;

            /**
             * Encodes the specified AudioStreamFinal message. Does not implicitly {@link fluent_dialogue_dora.v1.AudioStreamFinal.verify|verify} messages.
             * @param message AudioStreamFinal message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IAudioStreamFinal, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified AudioStreamFinal message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.AudioStreamFinal.verify|verify} messages.
             * @param message AudioStreamFinal message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IAudioStreamFinal, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an AudioStreamFinal message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns AudioStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.AudioStreamFinal;

            /**
             * Decodes an AudioStreamFinal message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns AudioStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.AudioStreamFinal;

            /**
             * Verifies an AudioStreamFinal message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates an AudioStreamFinal message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns AudioStreamFinal
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.AudioStreamFinal;

            /**
             * Creates a plain object from an AudioStreamFinal message. Also converts values to other types if specified.
             * @param message AudioStreamFinal
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.AudioStreamFinal, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this AudioStreamFinal to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for AudioStreamFinal
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** VoiceActivityState enum. */
        enum VoiceActivityState {
            VOICE_ACTIVITY_STATE_UNSPECIFIED = 0,
            VOICE_ACTIVITY_STATE_SILENCE = 1,
            VOICE_ACTIVITY_STATE_SPEECH = 2
        }

        /** TurnState enum. */
        enum TurnState {
            TURN_STATE_UNSPECIFIED = 0,
            TURN_STATE_IDLE = 1,
            TURN_STATE_STARTED = 2,
            TURN_STATE_ACTIVE = 3,
            TURN_STATE_ENDED = 4,
            TURN_STATE_CANCELLED = 5
        }

        /** Properties of a VoiceActivityEvent. */
        interface IVoiceActivityEvent {

            /** VoiceActivityEvent sourceId */
            sourceId?: (string|null);

            /** VoiceActivityEvent streamId */
            streamId?: (string|null);

            /** VoiceActivityEvent seq */
            seq?: (number|Long|null);

            /** VoiceActivityEvent sampleIndex */
            sampleIndex?: (number|Long|null);

            /** VoiceActivityEvent frameCount */
            frameCount?: (number|null);

            /** VoiceActivityEvent state */
            state?: (fluent_dialogue_dora.v1.VoiceActivityState|null);

            /** VoiceActivityEvent speechProbability */
            speechProbability?: (number|null);
        }

        /** Represents a VoiceActivityEvent. */
        class VoiceActivityEvent implements IVoiceActivityEvent {

            /**
             * Constructs a new VoiceActivityEvent.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IVoiceActivityEvent);

            /** VoiceActivityEvent sourceId. */
            public sourceId: string;

            /** VoiceActivityEvent streamId. */
            public streamId: string;

            /** VoiceActivityEvent seq. */
            public seq: (number|Long);

            /** VoiceActivityEvent sampleIndex. */
            public sampleIndex: (number|Long);

            /** VoiceActivityEvent frameCount. */
            public frameCount: number;

            /** VoiceActivityEvent state. */
            public state: fluent_dialogue_dora.v1.VoiceActivityState;

            /** VoiceActivityEvent speechProbability. */
            public speechProbability: number;

            /**
             * Creates a new VoiceActivityEvent instance using the specified properties.
             * @param [properties] Properties to set
             * @returns VoiceActivityEvent instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IVoiceActivityEvent): fluent_dialogue_dora.v1.VoiceActivityEvent;

            /**
             * Encodes the specified VoiceActivityEvent message. Does not implicitly {@link fluent_dialogue_dora.v1.VoiceActivityEvent.verify|verify} messages.
             * @param message VoiceActivityEvent message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IVoiceActivityEvent, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified VoiceActivityEvent message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.VoiceActivityEvent.verify|verify} messages.
             * @param message VoiceActivityEvent message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IVoiceActivityEvent, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a VoiceActivityEvent message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns VoiceActivityEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.VoiceActivityEvent;

            /**
             * Decodes a VoiceActivityEvent message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns VoiceActivityEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.VoiceActivityEvent;

            /**
             * Verifies a VoiceActivityEvent message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a VoiceActivityEvent message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns VoiceActivityEvent
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.VoiceActivityEvent;

            /**
             * Creates a plain object from a VoiceActivityEvent message. Also converts values to other types if specified.
             * @param message VoiceActivityEvent
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.VoiceActivityEvent, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this VoiceActivityEvent to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for VoiceActivityEvent
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an AudioLevelEvent. */
        interface IAudioLevelEvent {

            /** AudioLevelEvent sourceId */
            sourceId?: (string|null);

            /** AudioLevelEvent streamId */
            streamId?: (string|null);

            /** AudioLevelEvent seq */
            seq?: (number|Long|null);

            /** AudioLevelEvent sampleIndex */
            sampleIndex?: (number|Long|null);

            /** AudioLevelEvent frameCount */
            frameCount?: (number|null);

            /** AudioLevelEvent rmsDbfs */
            rmsDbfs?: (number|null);

            /** AudioLevelEvent peakDbfs */
            peakDbfs?: (number|null);

            /** AudioLevelEvent speechProbability */
            speechProbability?: (number|null);
        }

        /** Represents an AudioLevelEvent. */
        class AudioLevelEvent implements IAudioLevelEvent {

            /**
             * Constructs a new AudioLevelEvent.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IAudioLevelEvent);

            /** AudioLevelEvent sourceId. */
            public sourceId: string;

            /** AudioLevelEvent streamId. */
            public streamId: string;

            /** AudioLevelEvent seq. */
            public seq: (number|Long);

            /** AudioLevelEvent sampleIndex. */
            public sampleIndex: (number|Long);

            /** AudioLevelEvent frameCount. */
            public frameCount: number;

            /** AudioLevelEvent rmsDbfs. */
            public rmsDbfs: number;

            /** AudioLevelEvent peakDbfs. */
            public peakDbfs: number;

            /** AudioLevelEvent speechProbability. */
            public speechProbability: number;

            /**
             * Creates a new AudioLevelEvent instance using the specified properties.
             * @param [properties] Properties to set
             * @returns AudioLevelEvent instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IAudioLevelEvent): fluent_dialogue_dora.v1.AudioLevelEvent;

            /**
             * Encodes the specified AudioLevelEvent message. Does not implicitly {@link fluent_dialogue_dora.v1.AudioLevelEvent.verify|verify} messages.
             * @param message AudioLevelEvent message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IAudioLevelEvent, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified AudioLevelEvent message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.AudioLevelEvent.verify|verify} messages.
             * @param message AudioLevelEvent message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IAudioLevelEvent, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an AudioLevelEvent message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns AudioLevelEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.AudioLevelEvent;

            /**
             * Decodes an AudioLevelEvent message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns AudioLevelEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.AudioLevelEvent;

            /**
             * Verifies an AudioLevelEvent message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates an AudioLevelEvent message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns AudioLevelEvent
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.AudioLevelEvent;

            /**
             * Creates a plain object from an AudioLevelEvent message. Also converts values to other types if specified.
             * @param message AudioLevelEvent
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.AudioLevelEvent, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this AudioLevelEvent to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for AudioLevelEvent
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a VoiceActivityStreamFinal. */
        interface IVoiceActivityStreamFinal {

            /** VoiceActivityStreamFinal sourceId */
            sourceId?: (string|null);

            /** VoiceActivityStreamFinal streamId */
            streamId?: (string|null);

            /** VoiceActivityStreamFinal seq */
            seq?: (number|Long|null);

            /** VoiceActivityStreamFinal sampleIndex */
            sampleIndex?: (number|Long|null);
        }

        /** Represents a VoiceActivityStreamFinal. */
        class VoiceActivityStreamFinal implements IVoiceActivityStreamFinal {

            /**
             * Constructs a new VoiceActivityStreamFinal.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IVoiceActivityStreamFinal);

            /** VoiceActivityStreamFinal sourceId. */
            public sourceId: string;

            /** VoiceActivityStreamFinal streamId. */
            public streamId: string;

            /** VoiceActivityStreamFinal seq. */
            public seq: (number|Long);

            /** VoiceActivityStreamFinal sampleIndex. */
            public sampleIndex: (number|Long);

            /**
             * Creates a new VoiceActivityStreamFinal instance using the specified properties.
             * @param [properties] Properties to set
             * @returns VoiceActivityStreamFinal instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IVoiceActivityStreamFinal): fluent_dialogue_dora.v1.VoiceActivityStreamFinal;

            /**
             * Encodes the specified VoiceActivityStreamFinal message. Does not implicitly {@link fluent_dialogue_dora.v1.VoiceActivityStreamFinal.verify|verify} messages.
             * @param message VoiceActivityStreamFinal message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IVoiceActivityStreamFinal, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified VoiceActivityStreamFinal message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.VoiceActivityStreamFinal.verify|verify} messages.
             * @param message VoiceActivityStreamFinal message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IVoiceActivityStreamFinal, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a VoiceActivityStreamFinal message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns VoiceActivityStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.VoiceActivityStreamFinal;

            /**
             * Decodes a VoiceActivityStreamFinal message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns VoiceActivityStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.VoiceActivityStreamFinal;

            /**
             * Verifies a VoiceActivityStreamFinal message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a VoiceActivityStreamFinal message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns VoiceActivityStreamFinal
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.VoiceActivityStreamFinal;

            /**
             * Creates a plain object from a VoiceActivityStreamFinal message. Also converts values to other types if specified.
             * @param message VoiceActivityStreamFinal
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.VoiceActivityStreamFinal, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this VoiceActivityStreamFinal to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for VoiceActivityStreamFinal
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a TurnEvent. */
        interface ITurnEvent {

            /** TurnEvent sessionId */
            sessionId?: (string|null);

            /** TurnEvent userTurnId */
            userTurnId?: (string|null);

            /** TurnEvent streamId */
            streamId?: (string|null);

            /** TurnEvent seq */
            seq?: (number|Long|null);

            /** TurnEvent sampleIndex */
            sampleIndex?: (number|Long|null);

            /** TurnEvent state */
            state?: (fluent_dialogue_dora.v1.TurnState|null);

            /** TurnEvent confidence */
            confidence?: (number|null);
        }

        /** Represents a TurnEvent. */
        class TurnEvent implements ITurnEvent {

            /**
             * Constructs a new TurnEvent.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.ITurnEvent);

            /** TurnEvent sessionId. */
            public sessionId: string;

            /** TurnEvent userTurnId. */
            public userTurnId: string;

            /** TurnEvent streamId. */
            public streamId: string;

            /** TurnEvent seq. */
            public seq: (number|Long);

            /** TurnEvent sampleIndex. */
            public sampleIndex: (number|Long);

            /** TurnEvent state. */
            public state: fluent_dialogue_dora.v1.TurnState;

            /** TurnEvent confidence. */
            public confidence?: (number|null);

            /**
             * Creates a new TurnEvent instance using the specified properties.
             * @param [properties] Properties to set
             * @returns TurnEvent instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.ITurnEvent): fluent_dialogue_dora.v1.TurnEvent;

            /**
             * Encodes the specified TurnEvent message. Does not implicitly {@link fluent_dialogue_dora.v1.TurnEvent.verify|verify} messages.
             * @param message TurnEvent message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.ITurnEvent, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified TurnEvent message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.TurnEvent.verify|verify} messages.
             * @param message TurnEvent message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.ITurnEvent, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a TurnEvent message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns TurnEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.TurnEvent;

            /**
             * Decodes a TurnEvent message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns TurnEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.TurnEvent;

            /**
             * Verifies a TurnEvent message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a TurnEvent message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns TurnEvent
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.TurnEvent;

            /**
             * Creates a plain object from a TurnEvent message. Also converts values to other types if specified.
             * @param message TurnEvent
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.TurnEvent, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this TurnEvent to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for TurnEvent
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a TurnStreamFinal. */
        interface ITurnStreamFinal {

            /** TurnStreamFinal sessionId */
            sessionId?: (string|null);

            /** TurnStreamFinal streamId */
            streamId?: (string|null);

            /** TurnStreamFinal seq */
            seq?: (number|Long|null);

            /** TurnStreamFinal sampleIndex */
            sampleIndex?: (number|Long|null);
        }

        /** Represents a TurnStreamFinal. */
        class TurnStreamFinal implements ITurnStreamFinal {

            /**
             * Constructs a new TurnStreamFinal.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.ITurnStreamFinal);

            /** TurnStreamFinal sessionId. */
            public sessionId: string;

            /** TurnStreamFinal streamId. */
            public streamId: string;

            /** TurnStreamFinal seq. */
            public seq: (number|Long);

            /** TurnStreamFinal sampleIndex. */
            public sampleIndex: (number|Long);

            /**
             * Creates a new TurnStreamFinal instance using the specified properties.
             * @param [properties] Properties to set
             * @returns TurnStreamFinal instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.ITurnStreamFinal): fluent_dialogue_dora.v1.TurnStreamFinal;

            /**
             * Encodes the specified TurnStreamFinal message. Does not implicitly {@link fluent_dialogue_dora.v1.TurnStreamFinal.verify|verify} messages.
             * @param message TurnStreamFinal message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.ITurnStreamFinal, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified TurnStreamFinal message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.TurnStreamFinal.verify|verify} messages.
             * @param message TurnStreamFinal message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.ITurnStreamFinal, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a TurnStreamFinal message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns TurnStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.TurnStreamFinal;

            /**
             * Decodes a TurnStreamFinal message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns TurnStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.TurnStreamFinal;

            /**
             * Verifies a TurnStreamFinal message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a TurnStreamFinal message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns TurnStreamFinal
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.TurnStreamFinal;

            /**
             * Creates a plain object from a TurnStreamFinal message. Also converts values to other types if specified.
             * @param message TurnStreamFinal
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.TurnStreamFinal, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this TurnStreamFinal to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for TurnStreamFinal
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an AsrStart. */
        interface IAsrStart {

            /** AsrStart sessionId */
            sessionId?: (string|null);

            /** AsrStart userTurnId */
            userTurnId?: (string|null);

            /** AsrStart streamId */
            streamId?: (string|null);

            /** AsrStart seq */
            seq?: (number|Long|null);

            /** AsrStart startSampleIndex */
            startSampleIndex?: (number|Long|null);
        }

        /** Represents an AsrStart. */
        class AsrStart implements IAsrStart {

            /**
             * Constructs a new AsrStart.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IAsrStart);

            /** AsrStart sessionId. */
            public sessionId: string;

            /** AsrStart userTurnId. */
            public userTurnId: string;

            /** AsrStart streamId. */
            public streamId: string;

            /** AsrStart seq. */
            public seq: (number|Long);

            /** AsrStart startSampleIndex. */
            public startSampleIndex: (number|Long);

            /**
             * Creates a new AsrStart instance using the specified properties.
             * @param [properties] Properties to set
             * @returns AsrStart instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IAsrStart): fluent_dialogue_dora.v1.AsrStart;

            /**
             * Encodes the specified AsrStart message. Does not implicitly {@link fluent_dialogue_dora.v1.AsrStart.verify|verify} messages.
             * @param message AsrStart message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IAsrStart, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified AsrStart message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.AsrStart.verify|verify} messages.
             * @param message AsrStart message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IAsrStart, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an AsrStart message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns AsrStart
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.AsrStart;

            /**
             * Decodes an AsrStart message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns AsrStart
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.AsrStart;

            /**
             * Verifies an AsrStart message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates an AsrStart message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns AsrStart
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.AsrStart;

            /**
             * Creates a plain object from an AsrStart message. Also converts values to other types if specified.
             * @param message AsrStart
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.AsrStart, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this AsrStart to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for AsrStart
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an AsrStop. */
        interface IAsrStop {

            /** AsrStop sessionId */
            sessionId?: (string|null);

            /** AsrStop userTurnId */
            userTurnId?: (string|null);

            /** AsrStop streamId */
            streamId?: (string|null);

            /** AsrStop seq */
            seq?: (number|Long|null);

            /** AsrStop stopSampleIndex */
            stopSampleIndex?: (number|Long|null);
        }

        /** Represents an AsrStop. */
        class AsrStop implements IAsrStop {

            /**
             * Constructs a new AsrStop.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IAsrStop);

            /** AsrStop sessionId. */
            public sessionId: string;

            /** AsrStop userTurnId. */
            public userTurnId: string;

            /** AsrStop streamId. */
            public streamId: string;

            /** AsrStop seq. */
            public seq: (number|Long);

            /** AsrStop stopSampleIndex. */
            public stopSampleIndex: (number|Long);

            /**
             * Creates a new AsrStop instance using the specified properties.
             * @param [properties] Properties to set
             * @returns AsrStop instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IAsrStop): fluent_dialogue_dora.v1.AsrStop;

            /**
             * Encodes the specified AsrStop message. Does not implicitly {@link fluent_dialogue_dora.v1.AsrStop.verify|verify} messages.
             * @param message AsrStop message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IAsrStop, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified AsrStop message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.AsrStop.verify|verify} messages.
             * @param message AsrStop message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IAsrStop, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an AsrStop message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns AsrStop
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.AsrStop;

            /**
             * Decodes an AsrStop message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns AsrStop
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.AsrStop;

            /**
             * Verifies an AsrStop message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates an AsrStop message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns AsrStop
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.AsrStop;

            /**
             * Creates a plain object from an AsrStop message. Also converts values to other types if specified.
             * @param message AsrStop
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.AsrStop, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this AsrStop to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for AsrStop
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an AsrCancel. */
        interface IAsrCancel {

            /** AsrCancel sessionId */
            sessionId?: (string|null);

            /** AsrCancel userTurnId */
            userTurnId?: (string|null);

            /** AsrCancel streamId */
            streamId?: (string|null);

            /** AsrCancel seq */
            seq?: (number|Long|null);

            /** AsrCancel reason */
            reason?: (string|null);
        }

        /** Represents an AsrCancel. */
        class AsrCancel implements IAsrCancel {

            /**
             * Constructs a new AsrCancel.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IAsrCancel);

            /** AsrCancel sessionId. */
            public sessionId: string;

            /** AsrCancel userTurnId. */
            public userTurnId: string;

            /** AsrCancel streamId. */
            public streamId: string;

            /** AsrCancel seq. */
            public seq: (number|Long);

            /** AsrCancel reason. */
            public reason: string;

            /**
             * Creates a new AsrCancel instance using the specified properties.
             * @param [properties] Properties to set
             * @returns AsrCancel instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IAsrCancel): fluent_dialogue_dora.v1.AsrCancel;

            /**
             * Encodes the specified AsrCancel message. Does not implicitly {@link fluent_dialogue_dora.v1.AsrCancel.verify|verify} messages.
             * @param message AsrCancel message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IAsrCancel, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified AsrCancel message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.AsrCancel.verify|verify} messages.
             * @param message AsrCancel message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IAsrCancel, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an AsrCancel message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns AsrCancel
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.AsrCancel;

            /**
             * Decodes an AsrCancel message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns AsrCancel
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.AsrCancel;

            /**
             * Verifies an AsrCancel message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates an AsrCancel message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns AsrCancel
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.AsrCancel;

            /**
             * Creates a plain object from an AsrCancel message. Also converts values to other types if specified.
             * @param message AsrCancel
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.AsrCancel, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this AsrCancel to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for AsrCancel
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an AsrControl. */
        interface IAsrControl {

            /** AsrControl start */
            start?: (fluent_dialogue_dora.v1.IAsrStart|null);

            /** AsrControl stop */
            stop?: (fluent_dialogue_dora.v1.IAsrStop|null);

            /** AsrControl cancel */
            cancel?: (fluent_dialogue_dora.v1.IAsrCancel|null);
        }

        /** Represents an AsrControl. */
        class AsrControl implements IAsrControl {

            /**
             * Constructs a new AsrControl.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IAsrControl);

            /** AsrControl start. */
            public start?: (fluent_dialogue_dora.v1.IAsrStart|null);

            /** AsrControl stop. */
            public stop?: (fluent_dialogue_dora.v1.IAsrStop|null);

            /** AsrControl cancel. */
            public cancel?: (fluent_dialogue_dora.v1.IAsrCancel|null);

            /** AsrControl control. */
            public control?: ("start"|"stop"|"cancel");

            /**
             * Creates a new AsrControl instance using the specified properties.
             * @param [properties] Properties to set
             * @returns AsrControl instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IAsrControl): fluent_dialogue_dora.v1.AsrControl;

            /**
             * Encodes the specified AsrControl message. Does not implicitly {@link fluent_dialogue_dora.v1.AsrControl.verify|verify} messages.
             * @param message AsrControl message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IAsrControl, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified AsrControl message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.AsrControl.verify|verify} messages.
             * @param message AsrControl message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IAsrControl, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an AsrControl message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns AsrControl
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.AsrControl;

            /**
             * Decodes an AsrControl message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns AsrControl
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.AsrControl;

            /**
             * Verifies an AsrControl message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates an AsrControl message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns AsrControl
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.AsrControl;

            /**
             * Creates a plain object from an AsrControl message. Also converts values to other types if specified.
             * @param message AsrControl
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.AsrControl, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this AsrControl to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for AsrControl
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an AsrControlStreamFinal. */
        interface IAsrControlStreamFinal {

            /** AsrControlStreamFinal sessionId */
            sessionId?: (string|null);

            /** AsrControlStreamFinal streamId */
            streamId?: (string|null);

            /** AsrControlStreamFinal seq */
            seq?: (number|Long|null);
        }

        /** Represents an AsrControlStreamFinal. */
        class AsrControlStreamFinal implements IAsrControlStreamFinal {

            /**
             * Constructs a new AsrControlStreamFinal.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IAsrControlStreamFinal);

            /** AsrControlStreamFinal sessionId. */
            public sessionId: string;

            /** AsrControlStreamFinal streamId. */
            public streamId: string;

            /** AsrControlStreamFinal seq. */
            public seq: (number|Long);

            /**
             * Creates a new AsrControlStreamFinal instance using the specified properties.
             * @param [properties] Properties to set
             * @returns AsrControlStreamFinal instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IAsrControlStreamFinal): fluent_dialogue_dora.v1.AsrControlStreamFinal;

            /**
             * Encodes the specified AsrControlStreamFinal message. Does not implicitly {@link fluent_dialogue_dora.v1.AsrControlStreamFinal.verify|verify} messages.
             * @param message AsrControlStreamFinal message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IAsrControlStreamFinal, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified AsrControlStreamFinal message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.AsrControlStreamFinal.verify|verify} messages.
             * @param message AsrControlStreamFinal message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IAsrControlStreamFinal, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an AsrControlStreamFinal message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns AsrControlStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.AsrControlStreamFinal;

            /**
             * Decodes an AsrControlStreamFinal message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns AsrControlStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.AsrControlStreamFinal;

            /**
             * Verifies an AsrControlStreamFinal message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates an AsrControlStreamFinal message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns AsrControlStreamFinal
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.AsrControlStreamFinal;

            /**
             * Creates a plain object from an AsrControlStreamFinal message. Also converts values to other types if specified.
             * @param message AsrControlStreamFinal
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.AsrControlStreamFinal, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this AsrControlStreamFinal to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for AsrControlStreamFinal
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a TranscriptDelta. */
        interface ITranscriptDelta {

            /** TranscriptDelta sessionId */
            sessionId?: (string|null);

            /** TranscriptDelta userTurnId */
            userTurnId?: (string|null);

            /** TranscriptDelta streamId */
            streamId?: (string|null);

            /** TranscriptDelta seq */
            seq?: (number|Long|null);

            /** TranscriptDelta text */
            text?: (string|null);
        }

        /** Represents a TranscriptDelta. */
        class TranscriptDelta implements ITranscriptDelta {

            /**
             * Constructs a new TranscriptDelta.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.ITranscriptDelta);

            /** TranscriptDelta sessionId. */
            public sessionId: string;

            /** TranscriptDelta userTurnId. */
            public userTurnId: string;

            /** TranscriptDelta streamId. */
            public streamId: string;

            /** TranscriptDelta seq. */
            public seq: (number|Long);

            /** TranscriptDelta text. */
            public text: string;

            /**
             * Creates a new TranscriptDelta instance using the specified properties.
             * @param [properties] Properties to set
             * @returns TranscriptDelta instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.ITranscriptDelta): fluent_dialogue_dora.v1.TranscriptDelta;

            /**
             * Encodes the specified TranscriptDelta message. Does not implicitly {@link fluent_dialogue_dora.v1.TranscriptDelta.verify|verify} messages.
             * @param message TranscriptDelta message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.ITranscriptDelta, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified TranscriptDelta message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.TranscriptDelta.verify|verify} messages.
             * @param message TranscriptDelta message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.ITranscriptDelta, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a TranscriptDelta message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns TranscriptDelta
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.TranscriptDelta;

            /**
             * Decodes a TranscriptDelta message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns TranscriptDelta
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.TranscriptDelta;

            /**
             * Verifies a TranscriptDelta message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a TranscriptDelta message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns TranscriptDelta
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.TranscriptDelta;

            /**
             * Creates a plain object from a TranscriptDelta message. Also converts values to other types if specified.
             * @param message TranscriptDelta
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.TranscriptDelta, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this TranscriptDelta to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for TranscriptDelta
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a TranscriptPartial. */
        interface ITranscriptPartial {

            /** TranscriptPartial sessionId */
            sessionId?: (string|null);

            /** TranscriptPartial userTurnId */
            userTurnId?: (string|null);

            /** TranscriptPartial streamId */
            streamId?: (string|null);

            /** TranscriptPartial seq */
            seq?: (number|Long|null);

            /** TranscriptPartial text */
            text?: (string|null);
        }

        /** Represents a TranscriptPartial. */
        class TranscriptPartial implements ITranscriptPartial {

            /**
             * Constructs a new TranscriptPartial.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.ITranscriptPartial);

            /** TranscriptPartial sessionId. */
            public sessionId: string;

            /** TranscriptPartial userTurnId. */
            public userTurnId: string;

            /** TranscriptPartial streamId. */
            public streamId: string;

            /** TranscriptPartial seq. */
            public seq: (number|Long);

            /** TranscriptPartial text. */
            public text: string;

            /**
             * Creates a new TranscriptPartial instance using the specified properties.
             * @param [properties] Properties to set
             * @returns TranscriptPartial instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.ITranscriptPartial): fluent_dialogue_dora.v1.TranscriptPartial;

            /**
             * Encodes the specified TranscriptPartial message. Does not implicitly {@link fluent_dialogue_dora.v1.TranscriptPartial.verify|verify} messages.
             * @param message TranscriptPartial message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.ITranscriptPartial, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified TranscriptPartial message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.TranscriptPartial.verify|verify} messages.
             * @param message TranscriptPartial message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.ITranscriptPartial, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a TranscriptPartial message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns TranscriptPartial
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.TranscriptPartial;

            /**
             * Decodes a TranscriptPartial message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns TranscriptPartial
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.TranscriptPartial;

            /**
             * Verifies a TranscriptPartial message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a TranscriptPartial message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns TranscriptPartial
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.TranscriptPartial;

            /**
             * Creates a plain object from a TranscriptPartial message. Also converts values to other types if specified.
             * @param message TranscriptPartial
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.TranscriptPartial, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this TranscriptPartial to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for TranscriptPartial
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a TranscriptFinal. */
        interface ITranscriptFinal {

            /** TranscriptFinal sessionId */
            sessionId?: (string|null);

            /** TranscriptFinal userTurnId */
            userTurnId?: (string|null);

            /** TranscriptFinal streamId */
            streamId?: (string|null);

            /** TranscriptFinal seq */
            seq?: (number|Long|null);

            /** TranscriptFinal text */
            text?: (string|null);

            /** TranscriptFinal startSampleIndex */
            startSampleIndex?: (number|Long|null);

            /** TranscriptFinal endSampleIndex */
            endSampleIndex?: (number|Long|null);
        }

        /** Represents a TranscriptFinal. */
        class TranscriptFinal implements ITranscriptFinal {

            /**
             * Constructs a new TranscriptFinal.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.ITranscriptFinal);

            /** TranscriptFinal sessionId. */
            public sessionId: string;

            /** TranscriptFinal userTurnId. */
            public userTurnId: string;

            /** TranscriptFinal streamId. */
            public streamId: string;

            /** TranscriptFinal seq. */
            public seq: (number|Long);

            /** TranscriptFinal text. */
            public text: string;

            /** TranscriptFinal startSampleIndex. */
            public startSampleIndex: (number|Long);

            /** TranscriptFinal endSampleIndex. */
            public endSampleIndex: (number|Long);

            /**
             * Creates a new TranscriptFinal instance using the specified properties.
             * @param [properties] Properties to set
             * @returns TranscriptFinal instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.ITranscriptFinal): fluent_dialogue_dora.v1.TranscriptFinal;

            /**
             * Encodes the specified TranscriptFinal message. Does not implicitly {@link fluent_dialogue_dora.v1.TranscriptFinal.verify|verify} messages.
             * @param message TranscriptFinal message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.ITranscriptFinal, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified TranscriptFinal message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.TranscriptFinal.verify|verify} messages.
             * @param message TranscriptFinal message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.ITranscriptFinal, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a TranscriptFinal message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns TranscriptFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.TranscriptFinal;

            /**
             * Decodes a TranscriptFinal message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns TranscriptFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.TranscriptFinal;

            /**
             * Verifies a TranscriptFinal message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a TranscriptFinal message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns TranscriptFinal
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.TranscriptFinal;

            /**
             * Creates a plain object from a TranscriptFinal message. Also converts values to other types if specified.
             * @param message TranscriptFinal
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.TranscriptFinal, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this TranscriptFinal to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for TranscriptFinal
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a TranscriptEvent. */
        interface ITranscriptEvent {

            /** TranscriptEvent delta */
            delta?: (fluent_dialogue_dora.v1.ITranscriptDelta|null);

            /** TranscriptEvent final */
            final?: (fluent_dialogue_dora.v1.ITranscriptFinal|null);

            /** TranscriptEvent partial */
            partial?: (fluent_dialogue_dora.v1.ITranscriptPartial|null);
        }

        /** Represents a TranscriptEvent. */
        class TranscriptEvent implements ITranscriptEvent {

            /**
             * Constructs a new TranscriptEvent.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.ITranscriptEvent);

            /** TranscriptEvent delta. */
            public delta?: (fluent_dialogue_dora.v1.ITranscriptDelta|null);

            /** TranscriptEvent final. */
            public final?: (fluent_dialogue_dora.v1.ITranscriptFinal|null);

            /** TranscriptEvent partial. */
            public partial?: (fluent_dialogue_dora.v1.ITranscriptPartial|null);

            /** TranscriptEvent event. */
            public event?: ("delta"|"final"|"partial");

            /**
             * Creates a new TranscriptEvent instance using the specified properties.
             * @param [properties] Properties to set
             * @returns TranscriptEvent instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.ITranscriptEvent): fluent_dialogue_dora.v1.TranscriptEvent;

            /**
             * Encodes the specified TranscriptEvent message. Does not implicitly {@link fluent_dialogue_dora.v1.TranscriptEvent.verify|verify} messages.
             * @param message TranscriptEvent message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.ITranscriptEvent, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified TranscriptEvent message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.TranscriptEvent.verify|verify} messages.
             * @param message TranscriptEvent message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.ITranscriptEvent, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a TranscriptEvent message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns TranscriptEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.TranscriptEvent;

            /**
             * Decodes a TranscriptEvent message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns TranscriptEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.TranscriptEvent;

            /**
             * Verifies a TranscriptEvent message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a TranscriptEvent message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns TranscriptEvent
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.TranscriptEvent;

            /**
             * Creates a plain object from a TranscriptEvent message. Also converts values to other types if specified.
             * @param message TranscriptEvent
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.TranscriptEvent, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this TranscriptEvent to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for TranscriptEvent
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a TranscriptStreamFinal. */
        interface ITranscriptStreamFinal {

            /** TranscriptStreamFinal sessionId */
            sessionId?: (string|null);

            /** TranscriptStreamFinal streamId */
            streamId?: (string|null);

            /** TranscriptStreamFinal seq */
            seq?: (number|Long|null);

            /** TranscriptStreamFinal sampleIndex */
            sampleIndex?: (number|Long|null);
        }

        /** Represents a TranscriptStreamFinal. */
        class TranscriptStreamFinal implements ITranscriptStreamFinal {

            /**
             * Constructs a new TranscriptStreamFinal.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.ITranscriptStreamFinal);

            /** TranscriptStreamFinal sessionId. */
            public sessionId: string;

            /** TranscriptStreamFinal streamId. */
            public streamId: string;

            /** TranscriptStreamFinal seq. */
            public seq: (number|Long);

            /** TranscriptStreamFinal sampleIndex. */
            public sampleIndex: (number|Long);

            /**
             * Creates a new TranscriptStreamFinal instance using the specified properties.
             * @param [properties] Properties to set
             * @returns TranscriptStreamFinal instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.ITranscriptStreamFinal): fluent_dialogue_dora.v1.TranscriptStreamFinal;

            /**
             * Encodes the specified TranscriptStreamFinal message. Does not implicitly {@link fluent_dialogue_dora.v1.TranscriptStreamFinal.verify|verify} messages.
             * @param message TranscriptStreamFinal message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.ITranscriptStreamFinal, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified TranscriptStreamFinal message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.TranscriptStreamFinal.verify|verify} messages.
             * @param message TranscriptStreamFinal message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.ITranscriptStreamFinal, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a TranscriptStreamFinal message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns TranscriptStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.TranscriptStreamFinal;

            /**
             * Decodes a TranscriptStreamFinal message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns TranscriptStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.TranscriptStreamFinal;

            /**
             * Verifies a TranscriptStreamFinal message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a TranscriptStreamFinal message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns TranscriptStreamFinal
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.TranscriptStreamFinal;

            /**
             * Creates a plain object from a TranscriptStreamFinal message. Also converts values to other types if specified.
             * @param message TranscriptStreamFinal
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.TranscriptStreamFinal, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this TranscriptStreamFinal to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for TranscriptStreamFinal
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** DialogueInputKind enum. */
        enum DialogueInputKind {
            DIALOGUE_INPUT_KIND_UNSPECIFIED = 0,
            DIALOGUE_INPUT_KIND_TRANSCRIPT_FINAL = 1,
            DIALOGUE_INPUT_KIND_CANCEL = 2,
            DIALOGUE_INPUT_KIND_PLAYBACK_DONE = 3
        }

        /** DialogueEventKind enum. */
        enum DialogueEventKind {
            DIALOGUE_EVENT_KIND_UNSPECIFIED = 0,
            DIALOGUE_EVENT_KIND_AGENT_TEXT = 1,
            DIALOGUE_EVENT_KIND_TTS_TEXT = 2,
            DIALOGUE_EVENT_KIND_APPROVAL_REQUESTED = 3,
            DIALOGUE_EVENT_KIND_USER_INPUT_REQUESTED = 4,
            DIALOGUE_EVENT_KIND_MCP_ELICITATION_REQUESTED = 5,
            DIALOGUE_EVENT_KIND_TOOL_EVENT = 6,
            DIALOGUE_EVENT_KIND_CANCELLED = 7,
            DIALOGUE_EVENT_KIND_ERROR = 8
        }

        /** AgentApprovalDecision enum. */
        enum AgentApprovalDecision {
            AGENT_APPROVAL_DECISION_UNSPECIFIED = 0,
            AGENT_APPROVAL_DECISION_ACCEPT = 1,
            AGENT_APPROVAL_DECISION_DECLINE = 2,
            AGENT_APPROVAL_DECISION_CANCEL = 3
        }

        /** AgentApprovalScope enum. */
        enum AgentApprovalScope {
            AGENT_APPROVAL_SCOPE_UNSPECIFIED = 0,
            AGENT_APPROVAL_SCOPE_TURN = 1,
            AGENT_APPROVAL_SCOPE_SESSION = 2
        }

        /** AgentToolEventKind enum. */
        enum AgentToolEventKind {
            AGENT_TOOL_EVENT_KIND_UNSPECIFIED = 0,
            AGENT_TOOL_EVENT_KIND_STARTED = 1,
            AGENT_TOOL_EVENT_KIND_COMPLETED = 2,
            AGENT_TOOL_EVENT_KIND_FAILED = 3
        }

        /** AgentTurnDoneStatus enum. */
        enum AgentTurnDoneStatus {
            AGENT_TURN_DONE_STATUS_UNSPECIFIED = 0,
            AGENT_TURN_DONE_STATUS_COMPLETED = 1,
            AGENT_TURN_DONE_STATUS_CANCELLED = 2,
            AGENT_TURN_DONE_STATUS_FAILED = 3
        }

        /** Properties of a DialogueInput. */
        interface IDialogueInput {

            /** DialogueInput inputType */
            inputType?: (fluent_dialogue_dora.v1.DialogueInputKind|null);

            /** DialogueInput sessionId */
            sessionId?: (string|null);

            /** DialogueInput userTurnId */
            userTurnId?: (string|null);

            /** DialogueInput seq */
            seq?: (number|Long|null);

            /** DialogueInput text */
            text?: (string|null);

            /** DialogueInput requestId */
            requestId?: (string|null);
        }

        /** Represents a DialogueInput. */
        class DialogueInput implements IDialogueInput {

            /**
             * Constructs a new DialogueInput.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IDialogueInput);

            /** DialogueInput inputType. */
            public inputType: fluent_dialogue_dora.v1.DialogueInputKind;

            /** DialogueInput sessionId. */
            public sessionId: string;

            /** DialogueInput userTurnId. */
            public userTurnId: string;

            /** DialogueInput seq. */
            public seq: (number|Long);

            /** DialogueInput text. */
            public text?: (string|null);

            /** DialogueInput requestId. */
            public requestId?: (string|null);

            /**
             * Creates a new DialogueInput instance using the specified properties.
             * @param [properties] Properties to set
             * @returns DialogueInput instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IDialogueInput): fluent_dialogue_dora.v1.DialogueInput;

            /**
             * Encodes the specified DialogueInput message. Does not implicitly {@link fluent_dialogue_dora.v1.DialogueInput.verify|verify} messages.
             * @param message DialogueInput message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IDialogueInput, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified DialogueInput message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.DialogueInput.verify|verify} messages.
             * @param message DialogueInput message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IDialogueInput, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a DialogueInput message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns DialogueInput
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.DialogueInput;

            /**
             * Decodes a DialogueInput message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns DialogueInput
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.DialogueInput;

            /**
             * Verifies a DialogueInput message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a DialogueInput message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns DialogueInput
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.DialogueInput;

            /**
             * Creates a plain object from a DialogueInput message. Also converts values to other types if specified.
             * @param message DialogueInput
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.DialogueInput, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this DialogueInput to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for DialogueInput
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a DialogueEvent. */
        interface IDialogueEvent {

            /** DialogueEvent event */
            event?: (fluent_dialogue_dora.v1.DialogueEventKind|null);

            /** DialogueEvent sessionId */
            sessionId?: (string|null);

            /** DialogueEvent userTurnId */
            userTurnId?: (string|null);

            /** DialogueEvent seq */
            seq?: (number|Long|null);

            /** DialogueEvent text */
            text?: (string|null);

            /** DialogueEvent requestId */
            requestId?: (string|null);

            /** DialogueEvent message */
            message?: (string|null);
        }

        /** Represents a DialogueEvent. */
        class DialogueEvent implements IDialogueEvent {

            /**
             * Constructs a new DialogueEvent.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IDialogueEvent);

            /** DialogueEvent event. */
            public event: fluent_dialogue_dora.v1.DialogueEventKind;

            /** DialogueEvent sessionId. */
            public sessionId: string;

            /** DialogueEvent userTurnId. */
            public userTurnId: string;

            /** DialogueEvent seq. */
            public seq: (number|Long);

            /** DialogueEvent text. */
            public text?: (string|null);

            /** DialogueEvent requestId. */
            public requestId?: (string|null);

            /** DialogueEvent message. */
            public message?: (string|null);

            /**
             * Creates a new DialogueEvent instance using the specified properties.
             * @param [properties] Properties to set
             * @returns DialogueEvent instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IDialogueEvent): fluent_dialogue_dora.v1.DialogueEvent;

            /**
             * Encodes the specified DialogueEvent message. Does not implicitly {@link fluent_dialogue_dora.v1.DialogueEvent.verify|verify} messages.
             * @param message DialogueEvent message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IDialogueEvent, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified DialogueEvent message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.DialogueEvent.verify|verify} messages.
             * @param message DialogueEvent message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IDialogueEvent, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a DialogueEvent message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns DialogueEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.DialogueEvent;

            /**
             * Decodes a DialogueEvent message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns DialogueEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.DialogueEvent;

            /**
             * Verifies a DialogueEvent message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a DialogueEvent message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns DialogueEvent
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.DialogueEvent;

            /**
             * Creates a plain object from a DialogueEvent message. Also converts values to other types if specified.
             * @param message DialogueEvent
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.DialogueEvent, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this DialogueEvent to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for DialogueEvent
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an AgentTurnRequest. */
        interface IAgentTurnRequest {

            /** AgentTurnRequest sessionId */
            sessionId?: (string|null);

            /** AgentTurnRequest userTurnId */
            userTurnId?: (string|null);

            /** AgentTurnRequest assistantTurnId */
            assistantTurnId?: (string|null);

            /** AgentTurnRequest seq */
            seq?: (number|Long|null);

            /** AgentTurnRequest text */
            text?: (string|null);
        }

        /** Represents an AgentTurnRequest. */
        class AgentTurnRequest implements IAgentTurnRequest {

            /**
             * Constructs a new AgentTurnRequest.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IAgentTurnRequest);

            /** AgentTurnRequest sessionId. */
            public sessionId: string;

            /** AgentTurnRequest userTurnId. */
            public userTurnId: string;

            /** AgentTurnRequest assistantTurnId. */
            public assistantTurnId: string;

            /** AgentTurnRequest seq. */
            public seq: (number|Long);

            /** AgentTurnRequest text. */
            public text: string;

            /**
             * Creates a new AgentTurnRequest instance using the specified properties.
             * @param [properties] Properties to set
             * @returns AgentTurnRequest instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IAgentTurnRequest): fluent_dialogue_dora.v1.AgentTurnRequest;

            /**
             * Encodes the specified AgentTurnRequest message. Does not implicitly {@link fluent_dialogue_dora.v1.AgentTurnRequest.verify|verify} messages.
             * @param message AgentTurnRequest message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IAgentTurnRequest, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified AgentTurnRequest message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.AgentTurnRequest.verify|verify} messages.
             * @param message AgentTurnRequest message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IAgentTurnRequest, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an AgentTurnRequest message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns AgentTurnRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.AgentTurnRequest;

            /**
             * Decodes an AgentTurnRequest message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns AgentTurnRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.AgentTurnRequest;

            /**
             * Verifies an AgentTurnRequest message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates an AgentTurnRequest message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns AgentTurnRequest
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.AgentTurnRequest;

            /**
             * Creates a plain object from an AgentTurnRequest message. Also converts values to other types if specified.
             * @param message AgentTurnRequest
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.AgentTurnRequest, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this AgentTurnRequest to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for AgentTurnRequest
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an AgentTextDelta. */
        interface IAgentTextDelta {

            /** AgentTextDelta sessionId */
            sessionId?: (string|null);

            /** AgentTextDelta userTurnId */
            userTurnId?: (string|null);

            /** AgentTextDelta agentTurnId */
            agentTurnId?: (string|null);

            /** AgentTextDelta seq */
            seq?: (number|Long|null);

            /** AgentTextDelta text */
            text?: (string|null);
        }

        /** Represents an AgentTextDelta. */
        class AgentTextDelta implements IAgentTextDelta {

            /**
             * Constructs a new AgentTextDelta.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IAgentTextDelta);

            /** AgentTextDelta sessionId. */
            public sessionId: string;

            /** AgentTextDelta userTurnId. */
            public userTurnId: string;

            /** AgentTextDelta agentTurnId. */
            public agentTurnId: string;

            /** AgentTextDelta seq. */
            public seq: (number|Long);

            /** AgentTextDelta text. */
            public text: string;

            /**
             * Creates a new AgentTextDelta instance using the specified properties.
             * @param [properties] Properties to set
             * @returns AgentTextDelta instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IAgentTextDelta): fluent_dialogue_dora.v1.AgentTextDelta;

            /**
             * Encodes the specified AgentTextDelta message. Does not implicitly {@link fluent_dialogue_dora.v1.AgentTextDelta.verify|verify} messages.
             * @param message AgentTextDelta message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IAgentTextDelta, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified AgentTextDelta message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.AgentTextDelta.verify|verify} messages.
             * @param message AgentTextDelta message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IAgentTextDelta, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an AgentTextDelta message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns AgentTextDelta
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.AgentTextDelta;

            /**
             * Decodes an AgentTextDelta message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns AgentTextDelta
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.AgentTextDelta;

            /**
             * Verifies an AgentTextDelta message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates an AgentTextDelta message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns AgentTextDelta
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.AgentTextDelta;

            /**
             * Creates a plain object from an AgentTextDelta message. Also converts values to other types if specified.
             * @param message AgentTextDelta
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.AgentTextDelta, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this AgentTextDelta to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for AgentTextDelta
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an AgentTurnDone. */
        interface IAgentTurnDone {

            /** AgentTurnDone sessionId */
            sessionId?: (string|null);

            /** AgentTurnDone userTurnId */
            userTurnId?: (string|null);

            /** AgentTurnDone agentTurnId */
            agentTurnId?: (string|null);

            /** AgentTurnDone seq */
            seq?: (number|Long|null);

            /** AgentTurnDone status */
            status?: (fluent_dialogue_dora.v1.AgentTurnDoneStatus|null);

            /** AgentTurnDone reason */
            reason?: (string|null);
        }

        /** Represents an AgentTurnDone. */
        class AgentTurnDone implements IAgentTurnDone {

            /**
             * Constructs a new AgentTurnDone.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IAgentTurnDone);

            /** AgentTurnDone sessionId. */
            public sessionId: string;

            /** AgentTurnDone userTurnId. */
            public userTurnId: string;

            /** AgentTurnDone agentTurnId. */
            public agentTurnId: string;

            /** AgentTurnDone seq. */
            public seq: (number|Long);

            /** AgentTurnDone status. */
            public status: fluent_dialogue_dora.v1.AgentTurnDoneStatus;

            /** AgentTurnDone reason. */
            public reason?: (string|null);

            /**
             * Creates a new AgentTurnDone instance using the specified properties.
             * @param [properties] Properties to set
             * @returns AgentTurnDone instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IAgentTurnDone): fluent_dialogue_dora.v1.AgentTurnDone;

            /**
             * Encodes the specified AgentTurnDone message. Does not implicitly {@link fluent_dialogue_dora.v1.AgentTurnDone.verify|verify} messages.
             * @param message AgentTurnDone message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IAgentTurnDone, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified AgentTurnDone message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.AgentTurnDone.verify|verify} messages.
             * @param message AgentTurnDone message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IAgentTurnDone, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an AgentTurnDone message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns AgentTurnDone
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.AgentTurnDone;

            /**
             * Decodes an AgentTurnDone message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns AgentTurnDone
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.AgentTurnDone;

            /**
             * Verifies an AgentTurnDone message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates an AgentTurnDone message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns AgentTurnDone
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.AgentTurnDone;

            /**
             * Creates a plain object from an AgentTurnDone message. Also converts values to other types if specified.
             * @param message AgentTurnDone
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.AgentTurnDone, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this AgentTurnDone to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for AgentTurnDone
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an AgentApprovalRequest. */
        interface IAgentApprovalRequest {

            /** AgentApprovalRequest sessionId */
            sessionId?: (string|null);

            /** AgentApprovalRequest userTurnId */
            userTurnId?: (string|null);

            /** AgentApprovalRequest approvalId */
            approvalId?: (string|null);

            /** AgentApprovalRequest seq */
            seq?: (number|Long|null);

            /** AgentApprovalRequest prompt */
            prompt?: (string|null);

            /** AgentApprovalRequest actionLabel */
            actionLabel?: (string|null);
        }

        /** Represents an AgentApprovalRequest. */
        class AgentApprovalRequest implements IAgentApprovalRequest {

            /**
             * Constructs a new AgentApprovalRequest.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IAgentApprovalRequest);

            /** AgentApprovalRequest sessionId. */
            public sessionId: string;

            /** AgentApprovalRequest userTurnId. */
            public userTurnId: string;

            /** AgentApprovalRequest approvalId. */
            public approvalId: string;

            /** AgentApprovalRequest seq. */
            public seq: (number|Long);

            /** AgentApprovalRequest prompt. */
            public prompt: string;

            /** AgentApprovalRequest actionLabel. */
            public actionLabel: string;

            /**
             * Creates a new AgentApprovalRequest instance using the specified properties.
             * @param [properties] Properties to set
             * @returns AgentApprovalRequest instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IAgentApprovalRequest): fluent_dialogue_dora.v1.AgentApprovalRequest;

            /**
             * Encodes the specified AgentApprovalRequest message. Does not implicitly {@link fluent_dialogue_dora.v1.AgentApprovalRequest.verify|verify} messages.
             * @param message AgentApprovalRequest message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IAgentApprovalRequest, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified AgentApprovalRequest message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.AgentApprovalRequest.verify|verify} messages.
             * @param message AgentApprovalRequest message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IAgentApprovalRequest, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an AgentApprovalRequest message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns AgentApprovalRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.AgentApprovalRequest;

            /**
             * Decodes an AgentApprovalRequest message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns AgentApprovalRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.AgentApprovalRequest;

            /**
             * Verifies an AgentApprovalRequest message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates an AgentApprovalRequest message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns AgentApprovalRequest
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.AgentApprovalRequest;

            /**
             * Creates a plain object from an AgentApprovalRequest message. Also converts values to other types if specified.
             * @param message AgentApprovalRequest
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.AgentApprovalRequest, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this AgentApprovalRequest to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for AgentApprovalRequest
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an AgentApprovalResponse. */
        interface IAgentApprovalResponse {

            /** AgentApprovalResponse sessionId */
            sessionId?: (string|null);

            /** AgentApprovalResponse userTurnId */
            userTurnId?: (string|null);

            /** AgentApprovalResponse approvalId */
            approvalId?: (string|null);

            /** AgentApprovalResponse seq */
            seq?: (number|Long|null);

            /** AgentApprovalResponse decision */
            decision?: (fluent_dialogue_dora.v1.AgentApprovalDecision|null);

            /** AgentApprovalResponse scope */
            scope?: (fluent_dialogue_dora.v1.AgentApprovalScope|null);

            /** AgentApprovalResponse reason */
            reason?: (string|null);
        }

        /** Represents an AgentApprovalResponse. */
        class AgentApprovalResponse implements IAgentApprovalResponse {

            /**
             * Constructs a new AgentApprovalResponse.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IAgentApprovalResponse);

            /** AgentApprovalResponse sessionId. */
            public sessionId: string;

            /** AgentApprovalResponse userTurnId. */
            public userTurnId: string;

            /** AgentApprovalResponse approvalId. */
            public approvalId: string;

            /** AgentApprovalResponse seq. */
            public seq: (number|Long);

            /** AgentApprovalResponse decision. */
            public decision: fluent_dialogue_dora.v1.AgentApprovalDecision;

            /** AgentApprovalResponse scope. */
            public scope: fluent_dialogue_dora.v1.AgentApprovalScope;

            /** AgentApprovalResponse reason. */
            public reason?: (string|null);

            /**
             * Creates a new AgentApprovalResponse instance using the specified properties.
             * @param [properties] Properties to set
             * @returns AgentApprovalResponse instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IAgentApprovalResponse): fluent_dialogue_dora.v1.AgentApprovalResponse;

            /**
             * Encodes the specified AgentApprovalResponse message. Does not implicitly {@link fluent_dialogue_dora.v1.AgentApprovalResponse.verify|verify} messages.
             * @param message AgentApprovalResponse message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IAgentApprovalResponse, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified AgentApprovalResponse message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.AgentApprovalResponse.verify|verify} messages.
             * @param message AgentApprovalResponse message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IAgentApprovalResponse, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an AgentApprovalResponse message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns AgentApprovalResponse
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.AgentApprovalResponse;

            /**
             * Decodes an AgentApprovalResponse message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns AgentApprovalResponse
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.AgentApprovalResponse;

            /**
             * Verifies an AgentApprovalResponse message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates an AgentApprovalResponse message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns AgentApprovalResponse
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.AgentApprovalResponse;

            /**
             * Creates a plain object from an AgentApprovalResponse message. Also converts values to other types if specified.
             * @param message AgentApprovalResponse
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.AgentApprovalResponse, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this AgentApprovalResponse to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for AgentApprovalResponse
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an AgentToolEvent. */
        interface IAgentToolEvent {

            /** AgentToolEvent sessionId */
            sessionId?: (string|null);

            /** AgentToolEvent userTurnId */
            userTurnId?: (string|null);

            /** AgentToolEvent toolCallId */
            toolCallId?: (string|null);

            /** AgentToolEvent seq */
            seq?: (number|Long|null);

            /** AgentToolEvent event */
            event?: (fluent_dialogue_dora.v1.AgentToolEventKind|null);

            /** AgentToolEvent name */
            name?: (string|null);

            /** AgentToolEvent summary */
            summary?: (string|null);

            /** AgentToolEvent errorMessage */
            errorMessage?: (string|null);
        }

        /** Represents an AgentToolEvent. */
        class AgentToolEvent implements IAgentToolEvent {

            /**
             * Constructs a new AgentToolEvent.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IAgentToolEvent);

            /** AgentToolEvent sessionId. */
            public sessionId: string;

            /** AgentToolEvent userTurnId. */
            public userTurnId: string;

            /** AgentToolEvent toolCallId. */
            public toolCallId: string;

            /** AgentToolEvent seq. */
            public seq: (number|Long);

            /** AgentToolEvent event. */
            public event: fluent_dialogue_dora.v1.AgentToolEventKind;

            /** AgentToolEvent name. */
            public name: string;

            /** AgentToolEvent summary. */
            public summary?: (string|null);

            /** AgentToolEvent errorMessage. */
            public errorMessage?: (string|null);

            /**
             * Creates a new AgentToolEvent instance using the specified properties.
             * @param [properties] Properties to set
             * @returns AgentToolEvent instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IAgentToolEvent): fluent_dialogue_dora.v1.AgentToolEvent;

            /**
             * Encodes the specified AgentToolEvent message. Does not implicitly {@link fluent_dialogue_dora.v1.AgentToolEvent.verify|verify} messages.
             * @param message AgentToolEvent message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IAgentToolEvent, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified AgentToolEvent message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.AgentToolEvent.verify|verify} messages.
             * @param message AgentToolEvent message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IAgentToolEvent, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an AgentToolEvent message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns AgentToolEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.AgentToolEvent;

            /**
             * Decodes an AgentToolEvent message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns AgentToolEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.AgentToolEvent;

            /**
             * Verifies an AgentToolEvent message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates an AgentToolEvent message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns AgentToolEvent
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.AgentToolEvent;

            /**
             * Creates a plain object from an AgentToolEvent message. Also converts values to other types if specified.
             * @param message AgentToolEvent
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.AgentToolEvent, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this AgentToolEvent to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for AgentToolEvent
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an AgentCancelRequest. */
        interface IAgentCancelRequest {

            /** AgentCancelRequest sessionId */
            sessionId?: (string|null);

            /** AgentCancelRequest userTurnId */
            userTurnId?: (string|null);

            /** AgentCancelRequest seq */
            seq?: (number|Long|null);

            /** AgentCancelRequest reason */
            reason?: (string|null);

            /** AgentCancelRequest heardText */
            heardText?: (string|null);
        }

        /** Represents an AgentCancelRequest. */
        class AgentCancelRequest implements IAgentCancelRequest {

            /**
             * Constructs a new AgentCancelRequest.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IAgentCancelRequest);

            /** AgentCancelRequest sessionId. */
            public sessionId: string;

            /** AgentCancelRequest userTurnId. */
            public userTurnId: string;

            /** AgentCancelRequest seq. */
            public seq: (number|Long);

            /** AgentCancelRequest reason. */
            public reason?: (string|null);

            /** AgentCancelRequest heardText. */
            public heardText?: (string|null);

            /**
             * Creates a new AgentCancelRequest instance using the specified properties.
             * @param [properties] Properties to set
             * @returns AgentCancelRequest instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IAgentCancelRequest): fluent_dialogue_dora.v1.AgentCancelRequest;

            /**
             * Encodes the specified AgentCancelRequest message. Does not implicitly {@link fluent_dialogue_dora.v1.AgentCancelRequest.verify|verify} messages.
             * @param message AgentCancelRequest message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IAgentCancelRequest, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified AgentCancelRequest message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.AgentCancelRequest.verify|verify} messages.
             * @param message AgentCancelRequest message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IAgentCancelRequest, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an AgentCancelRequest message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns AgentCancelRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.AgentCancelRequest;

            /**
             * Decodes an AgentCancelRequest message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns AgentCancelRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.AgentCancelRequest;

            /**
             * Verifies an AgentCancelRequest message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates an AgentCancelRequest message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns AgentCancelRequest
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.AgentCancelRequest;

            /**
             * Creates a plain object from an AgentCancelRequest message. Also converts values to other types if specified.
             * @param message AgentCancelRequest
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.AgentCancelRequest, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this AgentCancelRequest to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for AgentCancelRequest
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an AgentUserInputOption. */
        interface IAgentUserInputOption {

            /** AgentUserInputOption label */
            label?: (string|null);

            /** AgentUserInputOption description */
            description?: (string|null);
        }

        /** Represents an AgentUserInputOption. */
        class AgentUserInputOption implements IAgentUserInputOption {

            /**
             * Constructs a new AgentUserInputOption.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IAgentUserInputOption);

            /** AgentUserInputOption label. */
            public label: string;

            /** AgentUserInputOption description. */
            public description: string;

            /**
             * Creates a new AgentUserInputOption instance using the specified properties.
             * @param [properties] Properties to set
             * @returns AgentUserInputOption instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IAgentUserInputOption): fluent_dialogue_dora.v1.AgentUserInputOption;

            /**
             * Encodes the specified AgentUserInputOption message. Does not implicitly {@link fluent_dialogue_dora.v1.AgentUserInputOption.verify|verify} messages.
             * @param message AgentUserInputOption message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IAgentUserInputOption, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified AgentUserInputOption message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.AgentUserInputOption.verify|verify} messages.
             * @param message AgentUserInputOption message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IAgentUserInputOption, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an AgentUserInputOption message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns AgentUserInputOption
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.AgentUserInputOption;

            /**
             * Decodes an AgentUserInputOption message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns AgentUserInputOption
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.AgentUserInputOption;

            /**
             * Verifies an AgentUserInputOption message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates an AgentUserInputOption message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns AgentUserInputOption
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.AgentUserInputOption;

            /**
             * Creates a plain object from an AgentUserInputOption message. Also converts values to other types if specified.
             * @param message AgentUserInputOption
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.AgentUserInputOption, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this AgentUserInputOption to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for AgentUserInputOption
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an AgentUserInputQuestion. */
        interface IAgentUserInputQuestion {

            /** AgentUserInputQuestion id */
            id?: (string|null);

            /** AgentUserInputQuestion header */
            header?: (string|null);

            /** AgentUserInputQuestion question */
            question?: (string|null);

            /** AgentUserInputQuestion isOther */
            isOther?: (boolean|null);

            /** AgentUserInputQuestion isSecret */
            isSecret?: (boolean|null);

            /** AgentUserInputQuestion options */
            options?: (fluent_dialogue_dora.v1.IAgentUserInputOption[]|null);
        }

        /** Represents an AgentUserInputQuestion. */
        class AgentUserInputQuestion implements IAgentUserInputQuestion {

            /**
             * Constructs a new AgentUserInputQuestion.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IAgentUserInputQuestion);

            /** AgentUserInputQuestion id. */
            public id: string;

            /** AgentUserInputQuestion header. */
            public header: string;

            /** AgentUserInputQuestion question. */
            public question: string;

            /** AgentUserInputQuestion isOther. */
            public isOther: boolean;

            /** AgentUserInputQuestion isSecret. */
            public isSecret: boolean;

            /** AgentUserInputQuestion options. */
            public options: fluent_dialogue_dora.v1.IAgentUserInputOption[];

            /**
             * Creates a new AgentUserInputQuestion instance using the specified properties.
             * @param [properties] Properties to set
             * @returns AgentUserInputQuestion instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IAgentUserInputQuestion): fluent_dialogue_dora.v1.AgentUserInputQuestion;

            /**
             * Encodes the specified AgentUserInputQuestion message. Does not implicitly {@link fluent_dialogue_dora.v1.AgentUserInputQuestion.verify|verify} messages.
             * @param message AgentUserInputQuestion message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IAgentUserInputQuestion, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified AgentUserInputQuestion message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.AgentUserInputQuestion.verify|verify} messages.
             * @param message AgentUserInputQuestion message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IAgentUserInputQuestion, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an AgentUserInputQuestion message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns AgentUserInputQuestion
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.AgentUserInputQuestion;

            /**
             * Decodes an AgentUserInputQuestion message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns AgentUserInputQuestion
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.AgentUserInputQuestion;

            /**
             * Verifies an AgentUserInputQuestion message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates an AgentUserInputQuestion message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns AgentUserInputQuestion
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.AgentUserInputQuestion;

            /**
             * Creates a plain object from an AgentUserInputQuestion message. Also converts values to other types if specified.
             * @param message AgentUserInputQuestion
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.AgentUserInputQuestion, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this AgentUserInputQuestion to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for AgentUserInputQuestion
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an AgentUserInputRequest. */
        interface IAgentUserInputRequest {

            /** AgentUserInputRequest sessionId */
            sessionId?: (string|null);

            /** AgentUserInputRequest userTurnId */
            userTurnId?: (string|null);

            /** AgentUserInputRequest requestId */
            requestId?: (string|null);

            /** AgentUserInputRequest seq */
            seq?: (number|Long|null);

            /** AgentUserInputRequest questions */
            questions?: (fluent_dialogue_dora.v1.IAgentUserInputQuestion[]|null);
        }

        /** Represents an AgentUserInputRequest. */
        class AgentUserInputRequest implements IAgentUserInputRequest {

            /**
             * Constructs a new AgentUserInputRequest.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IAgentUserInputRequest);

            /** AgentUserInputRequest sessionId. */
            public sessionId: string;

            /** AgentUserInputRequest userTurnId. */
            public userTurnId: string;

            /** AgentUserInputRequest requestId. */
            public requestId: string;

            /** AgentUserInputRequest seq. */
            public seq: (number|Long);

            /** AgentUserInputRequest questions. */
            public questions: fluent_dialogue_dora.v1.IAgentUserInputQuestion[];

            /**
             * Creates a new AgentUserInputRequest instance using the specified properties.
             * @param [properties] Properties to set
             * @returns AgentUserInputRequest instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IAgentUserInputRequest): fluent_dialogue_dora.v1.AgentUserInputRequest;

            /**
             * Encodes the specified AgentUserInputRequest message. Does not implicitly {@link fluent_dialogue_dora.v1.AgentUserInputRequest.verify|verify} messages.
             * @param message AgentUserInputRequest message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IAgentUserInputRequest, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified AgentUserInputRequest message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.AgentUserInputRequest.verify|verify} messages.
             * @param message AgentUserInputRequest message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IAgentUserInputRequest, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an AgentUserInputRequest message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns AgentUserInputRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.AgentUserInputRequest;

            /**
             * Decodes an AgentUserInputRequest message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns AgentUserInputRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.AgentUserInputRequest;

            /**
             * Verifies an AgentUserInputRequest message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates an AgentUserInputRequest message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns AgentUserInputRequest
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.AgentUserInputRequest;

            /**
             * Creates a plain object from an AgentUserInputRequest message. Also converts values to other types if specified.
             * @param message AgentUserInputRequest
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.AgentUserInputRequest, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this AgentUserInputRequest to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for AgentUserInputRequest
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an AgentUserInputAnswer. */
        interface IAgentUserInputAnswer {

            /** AgentUserInputAnswer questionId */
            questionId?: (string|null);

            /** AgentUserInputAnswer answers */
            answers?: (string[]|null);
        }

        /** Represents an AgentUserInputAnswer. */
        class AgentUserInputAnswer implements IAgentUserInputAnswer {

            /**
             * Constructs a new AgentUserInputAnswer.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IAgentUserInputAnswer);

            /** AgentUserInputAnswer questionId. */
            public questionId: string;

            /** AgentUserInputAnswer answers. */
            public answers: string[];

            /**
             * Creates a new AgentUserInputAnswer instance using the specified properties.
             * @param [properties] Properties to set
             * @returns AgentUserInputAnswer instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IAgentUserInputAnswer): fluent_dialogue_dora.v1.AgentUserInputAnswer;

            /**
             * Encodes the specified AgentUserInputAnswer message. Does not implicitly {@link fluent_dialogue_dora.v1.AgentUserInputAnswer.verify|verify} messages.
             * @param message AgentUserInputAnswer message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IAgentUserInputAnswer, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified AgentUserInputAnswer message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.AgentUserInputAnswer.verify|verify} messages.
             * @param message AgentUserInputAnswer message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IAgentUserInputAnswer, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an AgentUserInputAnswer message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns AgentUserInputAnswer
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.AgentUserInputAnswer;

            /**
             * Decodes an AgentUserInputAnswer message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns AgentUserInputAnswer
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.AgentUserInputAnswer;

            /**
             * Verifies an AgentUserInputAnswer message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates an AgentUserInputAnswer message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns AgentUserInputAnswer
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.AgentUserInputAnswer;

            /**
             * Creates a plain object from an AgentUserInputAnswer message. Also converts values to other types if specified.
             * @param message AgentUserInputAnswer
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.AgentUserInputAnswer, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this AgentUserInputAnswer to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for AgentUserInputAnswer
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an AgentUserInputResponse. */
        interface IAgentUserInputResponse {

            /** AgentUserInputResponse sessionId */
            sessionId?: (string|null);

            /** AgentUserInputResponse userTurnId */
            userTurnId?: (string|null);

            /** AgentUserInputResponse requestId */
            requestId?: (string|null);

            /** AgentUserInputResponse seq */
            seq?: (number|Long|null);

            /** AgentUserInputResponse answers */
            answers?: (fluent_dialogue_dora.v1.IAgentUserInputAnswer[]|null);
        }

        /** Represents an AgentUserInputResponse. */
        class AgentUserInputResponse implements IAgentUserInputResponse {

            /**
             * Constructs a new AgentUserInputResponse.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IAgentUserInputResponse);

            /** AgentUserInputResponse sessionId. */
            public sessionId: string;

            /** AgentUserInputResponse userTurnId. */
            public userTurnId: string;

            /** AgentUserInputResponse requestId. */
            public requestId: string;

            /** AgentUserInputResponse seq. */
            public seq: (number|Long);

            /** AgentUserInputResponse answers. */
            public answers: fluent_dialogue_dora.v1.IAgentUserInputAnswer[];

            /**
             * Creates a new AgentUserInputResponse instance using the specified properties.
             * @param [properties] Properties to set
             * @returns AgentUserInputResponse instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IAgentUserInputResponse): fluent_dialogue_dora.v1.AgentUserInputResponse;

            /**
             * Encodes the specified AgentUserInputResponse message. Does not implicitly {@link fluent_dialogue_dora.v1.AgentUserInputResponse.verify|verify} messages.
             * @param message AgentUserInputResponse message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IAgentUserInputResponse, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified AgentUserInputResponse message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.AgentUserInputResponse.verify|verify} messages.
             * @param message AgentUserInputResponse message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IAgentUserInputResponse, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an AgentUserInputResponse message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns AgentUserInputResponse
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.AgentUserInputResponse;

            /**
             * Decodes an AgentUserInputResponse message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns AgentUserInputResponse
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.AgentUserInputResponse;

            /**
             * Verifies an AgentUserInputResponse message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates an AgentUserInputResponse message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns AgentUserInputResponse
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.AgentUserInputResponse;

            /**
             * Creates a plain object from an AgentUserInputResponse message. Also converts values to other types if specified.
             * @param message AgentUserInputResponse
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.AgentUserInputResponse, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this AgentUserInputResponse to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for AgentUserInputResponse
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** AgentMcpElicitationMode enum. */
        enum AgentMcpElicitationMode {
            AGENT_MCP_ELICITATION_MODE_UNSPECIFIED = 0,
            AGENT_MCP_ELICITATION_MODE_FORM = 1,
            AGENT_MCP_ELICITATION_MODE_URL = 2
        }

        /** AgentMcpElicitationAction enum. */
        enum AgentMcpElicitationAction {
            AGENT_MCP_ELICITATION_ACTION_UNSPECIFIED = 0,
            AGENT_MCP_ELICITATION_ACTION_ACCEPT = 1,
            AGENT_MCP_ELICITATION_ACTION_DECLINE = 2,
            AGENT_MCP_ELICITATION_ACTION_CANCEL = 3
        }

        /** Properties of an AgentMcpElicitationRequest. */
        interface IAgentMcpElicitationRequest {

            /** AgentMcpElicitationRequest sessionId */
            sessionId?: (string|null);

            /** AgentMcpElicitationRequest userTurnId */
            userTurnId?: (string|null);

            /** AgentMcpElicitationRequest requestId */
            requestId?: (string|null);

            /** AgentMcpElicitationRequest seq */
            seq?: (number|Long|null);

            /** AgentMcpElicitationRequest serverName */
            serverName?: (string|null);

            /** AgentMcpElicitationRequest mode */
            mode?: (fluent_dialogue_dora.v1.AgentMcpElicitationMode|null);

            /** AgentMcpElicitationRequest message */
            message?: (string|null);

            /** AgentMcpElicitationRequest url */
            url?: (string|null);

            /** AgentMcpElicitationRequest elicitationId */
            elicitationId?: (string|null);

            /** AgentMcpElicitationRequest requestedSchema */
            requestedSchema?: (google.protobuf.IValue|null);

            /** AgentMcpElicitationRequest meta */
            meta?: (google.protobuf.IValue|null);
        }

        /** Represents an AgentMcpElicitationRequest. */
        class AgentMcpElicitationRequest implements IAgentMcpElicitationRequest {

            /**
             * Constructs a new AgentMcpElicitationRequest.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IAgentMcpElicitationRequest);

            /** AgentMcpElicitationRequest sessionId. */
            public sessionId: string;

            /** AgentMcpElicitationRequest userTurnId. */
            public userTurnId: string;

            /** AgentMcpElicitationRequest requestId. */
            public requestId: string;

            /** AgentMcpElicitationRequest seq. */
            public seq: (number|Long);

            /** AgentMcpElicitationRequest serverName. */
            public serverName: string;

            /** AgentMcpElicitationRequest mode. */
            public mode: fluent_dialogue_dora.v1.AgentMcpElicitationMode;

            /** AgentMcpElicitationRequest message. */
            public message: string;

            /** AgentMcpElicitationRequest url. */
            public url?: (string|null);

            /** AgentMcpElicitationRequest elicitationId. */
            public elicitationId?: (string|null);

            /** AgentMcpElicitationRequest requestedSchema. */
            public requestedSchema?: (google.protobuf.IValue|null);

            /** AgentMcpElicitationRequest meta. */
            public meta?: (google.protobuf.IValue|null);

            /**
             * Creates a new AgentMcpElicitationRequest instance using the specified properties.
             * @param [properties] Properties to set
             * @returns AgentMcpElicitationRequest instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IAgentMcpElicitationRequest): fluent_dialogue_dora.v1.AgentMcpElicitationRequest;

            /**
             * Encodes the specified AgentMcpElicitationRequest message. Does not implicitly {@link fluent_dialogue_dora.v1.AgentMcpElicitationRequest.verify|verify} messages.
             * @param message AgentMcpElicitationRequest message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IAgentMcpElicitationRequest, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified AgentMcpElicitationRequest message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.AgentMcpElicitationRequest.verify|verify} messages.
             * @param message AgentMcpElicitationRequest message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IAgentMcpElicitationRequest, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an AgentMcpElicitationRequest message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns AgentMcpElicitationRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.AgentMcpElicitationRequest;

            /**
             * Decodes an AgentMcpElicitationRequest message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns AgentMcpElicitationRequest
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.AgentMcpElicitationRequest;

            /**
             * Verifies an AgentMcpElicitationRequest message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates an AgentMcpElicitationRequest message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns AgentMcpElicitationRequest
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.AgentMcpElicitationRequest;

            /**
             * Creates a plain object from an AgentMcpElicitationRequest message. Also converts values to other types if specified.
             * @param message AgentMcpElicitationRequest
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.AgentMcpElicitationRequest, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this AgentMcpElicitationRequest to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for AgentMcpElicitationRequest
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of an AgentMcpElicitationResponse. */
        interface IAgentMcpElicitationResponse {

            /** AgentMcpElicitationResponse sessionId */
            sessionId?: (string|null);

            /** AgentMcpElicitationResponse userTurnId */
            userTurnId?: (string|null);

            /** AgentMcpElicitationResponse requestId */
            requestId?: (string|null);

            /** AgentMcpElicitationResponse seq */
            seq?: (number|Long|null);

            /** AgentMcpElicitationResponse action */
            action?: (fluent_dialogue_dora.v1.AgentMcpElicitationAction|null);

            /** AgentMcpElicitationResponse content */
            content?: (google.protobuf.IValue|null);

            /** AgentMcpElicitationResponse meta */
            meta?: (google.protobuf.IValue|null);
        }

        /** Represents an AgentMcpElicitationResponse. */
        class AgentMcpElicitationResponse implements IAgentMcpElicitationResponse {

            /**
             * Constructs a new AgentMcpElicitationResponse.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IAgentMcpElicitationResponse);

            /** AgentMcpElicitationResponse sessionId. */
            public sessionId: string;

            /** AgentMcpElicitationResponse userTurnId. */
            public userTurnId: string;

            /** AgentMcpElicitationResponse requestId. */
            public requestId: string;

            /** AgentMcpElicitationResponse seq. */
            public seq: (number|Long);

            /** AgentMcpElicitationResponse action. */
            public action: fluent_dialogue_dora.v1.AgentMcpElicitationAction;

            /** AgentMcpElicitationResponse content. */
            public content?: (google.protobuf.IValue|null);

            /** AgentMcpElicitationResponse meta. */
            public meta?: (google.protobuf.IValue|null);

            /**
             * Creates a new AgentMcpElicitationResponse instance using the specified properties.
             * @param [properties] Properties to set
             * @returns AgentMcpElicitationResponse instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IAgentMcpElicitationResponse): fluent_dialogue_dora.v1.AgentMcpElicitationResponse;

            /**
             * Encodes the specified AgentMcpElicitationResponse message. Does not implicitly {@link fluent_dialogue_dora.v1.AgentMcpElicitationResponse.verify|verify} messages.
             * @param message AgentMcpElicitationResponse message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IAgentMcpElicitationResponse, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified AgentMcpElicitationResponse message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.AgentMcpElicitationResponse.verify|verify} messages.
             * @param message AgentMcpElicitationResponse message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IAgentMcpElicitationResponse, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an AgentMcpElicitationResponse message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns AgentMcpElicitationResponse
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.AgentMcpElicitationResponse;

            /**
             * Decodes an AgentMcpElicitationResponse message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns AgentMcpElicitationResponse
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.AgentMcpElicitationResponse;

            /**
             * Verifies an AgentMcpElicitationResponse message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates an AgentMcpElicitationResponse message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns AgentMcpElicitationResponse
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.AgentMcpElicitationResponse;

            /**
             * Creates a plain object from an AgentMcpElicitationResponse message. Also converts values to other types if specified.
             * @param message AgentMcpElicitationResponse
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.AgentMcpElicitationResponse, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this AgentMcpElicitationResponse to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for AgentMcpElicitationResponse
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a TtsTextChunk. */
        interface ITtsTextChunk {

            /** TtsTextChunk requestId */
            requestId?: (string|null);

            /** TtsTextChunk sessionId */
            sessionId?: (string|null);

            /** TtsTextChunk userTurnId */
            userTurnId?: (string|null);

            /** TtsTextChunk assistantTurnId */
            assistantTurnId?: (string|null);

            /** TtsTextChunk seq */
            seq?: (number|Long|null);

            /** TtsTextChunk text */
            text?: (string|null);

            /** TtsTextChunk isFinal */
            isFinal?: (boolean|null);
        }

        /** Represents a TtsTextChunk. */
        class TtsTextChunk implements ITtsTextChunk {

            /**
             * Constructs a new TtsTextChunk.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.ITtsTextChunk);

            /** TtsTextChunk requestId. */
            public requestId: string;

            /** TtsTextChunk sessionId. */
            public sessionId: string;

            /** TtsTextChunk userTurnId. */
            public userTurnId: string;

            /** TtsTextChunk assistantTurnId. */
            public assistantTurnId: string;

            /** TtsTextChunk seq. */
            public seq: (number|Long);

            /** TtsTextChunk text. */
            public text: string;

            /** TtsTextChunk isFinal. */
            public isFinal: boolean;

            /**
             * Creates a new TtsTextChunk instance using the specified properties.
             * @param [properties] Properties to set
             * @returns TtsTextChunk instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.ITtsTextChunk): fluent_dialogue_dora.v1.TtsTextChunk;

            /**
             * Encodes the specified TtsTextChunk message. Does not implicitly {@link fluent_dialogue_dora.v1.TtsTextChunk.verify|verify} messages.
             * @param message TtsTextChunk message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.ITtsTextChunk, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified TtsTextChunk message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.TtsTextChunk.verify|verify} messages.
             * @param message TtsTextChunk message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.ITtsTextChunk, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a TtsTextChunk message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns TtsTextChunk
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.TtsTextChunk;

            /**
             * Decodes a TtsTextChunk message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns TtsTextChunk
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.TtsTextChunk;

            /**
             * Verifies a TtsTextChunk message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a TtsTextChunk message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns TtsTextChunk
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.TtsTextChunk;

            /**
             * Creates a plain object from a TtsTextChunk message. Also converts values to other types if specified.
             * @param message TtsTextChunk
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.TtsTextChunk, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this TtsTextChunk to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for TtsTextChunk
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a TtsTextStreamFinal. */
        interface ITtsTextStreamFinal {

            /** TtsTextStreamFinal sessionId */
            sessionId?: (string|null);

            /** TtsTextStreamFinal userTurnId */
            userTurnId?: (string|null);

            /** TtsTextStreamFinal assistantTurnId */
            assistantTurnId?: (string|null);

            /** TtsTextStreamFinal seq */
            seq?: (number|Long|null);
        }

        /** Represents a TtsTextStreamFinal. */
        class TtsTextStreamFinal implements ITtsTextStreamFinal {

            /**
             * Constructs a new TtsTextStreamFinal.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.ITtsTextStreamFinal);

            /** TtsTextStreamFinal sessionId. */
            public sessionId: string;

            /** TtsTextStreamFinal userTurnId. */
            public userTurnId: string;

            /** TtsTextStreamFinal assistantTurnId. */
            public assistantTurnId: string;

            /** TtsTextStreamFinal seq. */
            public seq: (number|Long);

            /**
             * Creates a new TtsTextStreamFinal instance using the specified properties.
             * @param [properties] Properties to set
             * @returns TtsTextStreamFinal instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.ITtsTextStreamFinal): fluent_dialogue_dora.v1.TtsTextStreamFinal;

            /**
             * Encodes the specified TtsTextStreamFinal message. Does not implicitly {@link fluent_dialogue_dora.v1.TtsTextStreamFinal.verify|verify} messages.
             * @param message TtsTextStreamFinal message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.ITtsTextStreamFinal, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified TtsTextStreamFinal message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.TtsTextStreamFinal.verify|verify} messages.
             * @param message TtsTextStreamFinal message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.ITtsTextStreamFinal, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a TtsTextStreamFinal message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns TtsTextStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.TtsTextStreamFinal;

            /**
             * Decodes a TtsTextStreamFinal message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns TtsTextStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.TtsTextStreamFinal;

            /**
             * Verifies a TtsTextStreamFinal message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a TtsTextStreamFinal message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns TtsTextStreamFinal
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.TtsTextStreamFinal;

            /**
             * Creates a plain object from a TtsTextStreamFinal message. Also converts values to other types if specified.
             * @param message TtsTextStreamFinal
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.TtsTextStreamFinal, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this TtsTextStreamFinal to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for TtsTextStreamFinal
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a SynthesizedAudioChunk. */
        interface ISynthesizedAudioChunk {

            /** SynthesizedAudioChunk requestId */
            requestId?: (string|null);

            /** SynthesizedAudioChunk sessionId */
            sessionId?: (string|null);

            /** SynthesizedAudioChunk userTurnId */
            userTurnId?: (string|null);

            /** SynthesizedAudioChunk assistantTurnId */
            assistantTurnId?: (string|null);

            /** SynthesizedAudioChunk seq */
            seq?: (number|Long|null);

            /** SynthesizedAudioChunk audio */
            audio?: (fluent_dialogue_dora.v1.IAudioFrame|null);
        }

        /** Represents a SynthesizedAudioChunk. */
        class SynthesizedAudioChunk implements ISynthesizedAudioChunk {

            /**
             * Constructs a new SynthesizedAudioChunk.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.ISynthesizedAudioChunk);

            /** SynthesizedAudioChunk requestId. */
            public requestId: string;

            /** SynthesizedAudioChunk sessionId. */
            public sessionId: string;

            /** SynthesizedAudioChunk userTurnId. */
            public userTurnId: string;

            /** SynthesizedAudioChunk assistantTurnId. */
            public assistantTurnId: string;

            /** SynthesizedAudioChunk seq. */
            public seq: (number|Long);

            /** SynthesizedAudioChunk audio. */
            public audio?: (fluent_dialogue_dora.v1.IAudioFrame|null);

            /**
             * Creates a new SynthesizedAudioChunk instance using the specified properties.
             * @param [properties] Properties to set
             * @returns SynthesizedAudioChunk instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.ISynthesizedAudioChunk): fluent_dialogue_dora.v1.SynthesizedAudioChunk;

            /**
             * Encodes the specified SynthesizedAudioChunk message. Does not implicitly {@link fluent_dialogue_dora.v1.SynthesizedAudioChunk.verify|verify} messages.
             * @param message SynthesizedAudioChunk message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.ISynthesizedAudioChunk, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified SynthesizedAudioChunk message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.SynthesizedAudioChunk.verify|verify} messages.
             * @param message SynthesizedAudioChunk message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.ISynthesizedAudioChunk, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a SynthesizedAudioChunk message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns SynthesizedAudioChunk
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.SynthesizedAudioChunk;

            /**
             * Decodes a SynthesizedAudioChunk message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns SynthesizedAudioChunk
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.SynthesizedAudioChunk;

            /**
             * Verifies a SynthesizedAudioChunk message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a SynthesizedAudioChunk message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns SynthesizedAudioChunk
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.SynthesizedAudioChunk;

            /**
             * Creates a plain object from a SynthesizedAudioChunk message. Also converts values to other types if specified.
             * @param message SynthesizedAudioChunk
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.SynthesizedAudioChunk, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this SynthesizedAudioChunk to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for SynthesizedAudioChunk
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a SynthesizedAudioStreamFinal. */
        interface ISynthesizedAudioStreamFinal {

            /** SynthesizedAudioStreamFinal requestId */
            requestId?: (string|null);

            /** SynthesizedAudioStreamFinal sessionId */
            sessionId?: (string|null);

            /** SynthesizedAudioStreamFinal userTurnId */
            userTurnId?: (string|null);

            /** SynthesizedAudioStreamFinal assistantTurnId */
            assistantTurnId?: (string|null);

            /** SynthesizedAudioStreamFinal seq */
            seq?: (number|Long|null);

            /** SynthesizedAudioStreamFinal audioSourceId */
            audioSourceId?: (string|null);

            /** SynthesizedAudioStreamFinal audioStreamId */
            audioStreamId?: (string|null);

            /** SynthesizedAudioStreamFinal audioSeq */
            audioSeq?: (number|Long|null);

            /** SynthesizedAudioStreamFinal audioSampleIndex */
            audioSampleIndex?: (number|Long|null);

            /** SynthesizedAudioStreamFinal audioCaptureTimeNs */
            audioCaptureTimeNs?: (number|Long|null);

            /** SynthesizedAudioStreamFinal audioFormat */
            audioFormat?: (fluent_dialogue_dora.v1.IAudioFormat|null);
        }

        /** Represents a SynthesizedAudioStreamFinal. */
        class SynthesizedAudioStreamFinal implements ISynthesizedAudioStreamFinal {

            /**
             * Constructs a new SynthesizedAudioStreamFinal.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.ISynthesizedAudioStreamFinal);

            /** SynthesizedAudioStreamFinal requestId. */
            public requestId: string;

            /** SynthesizedAudioStreamFinal sessionId. */
            public sessionId: string;

            /** SynthesizedAudioStreamFinal userTurnId. */
            public userTurnId: string;

            /** SynthesizedAudioStreamFinal assistantTurnId. */
            public assistantTurnId: string;

            /** SynthesizedAudioStreamFinal seq. */
            public seq: (number|Long);

            /** SynthesizedAudioStreamFinal audioSourceId. */
            public audioSourceId: string;

            /** SynthesizedAudioStreamFinal audioStreamId. */
            public audioStreamId: string;

            /** SynthesizedAudioStreamFinal audioSeq. */
            public audioSeq: (number|Long);

            /** SynthesizedAudioStreamFinal audioSampleIndex. */
            public audioSampleIndex: (number|Long);

            /** SynthesizedAudioStreamFinal audioCaptureTimeNs. */
            public audioCaptureTimeNs: (number|Long);

            /** SynthesizedAudioStreamFinal audioFormat. */
            public audioFormat?: (fluent_dialogue_dora.v1.IAudioFormat|null);

            /**
             * Creates a new SynthesizedAudioStreamFinal instance using the specified properties.
             * @param [properties] Properties to set
             * @returns SynthesizedAudioStreamFinal instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.ISynthesizedAudioStreamFinal): fluent_dialogue_dora.v1.SynthesizedAudioStreamFinal;

            /**
             * Encodes the specified SynthesizedAudioStreamFinal message. Does not implicitly {@link fluent_dialogue_dora.v1.SynthesizedAudioStreamFinal.verify|verify} messages.
             * @param message SynthesizedAudioStreamFinal message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.ISynthesizedAudioStreamFinal, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified SynthesizedAudioStreamFinal message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.SynthesizedAudioStreamFinal.verify|verify} messages.
             * @param message SynthesizedAudioStreamFinal message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.ISynthesizedAudioStreamFinal, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a SynthesizedAudioStreamFinal message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns SynthesizedAudioStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.SynthesizedAudioStreamFinal;

            /**
             * Decodes a SynthesizedAudioStreamFinal message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns SynthesizedAudioStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.SynthesizedAudioStreamFinal;

            /**
             * Verifies a SynthesizedAudioStreamFinal message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a SynthesizedAudioStreamFinal message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns SynthesizedAudioStreamFinal
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.SynthesizedAudioStreamFinal;

            /**
             * Creates a plain object from a SynthesizedAudioStreamFinal message. Also converts values to other types if specified.
             * @param message SynthesizedAudioStreamFinal
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.SynthesizedAudioStreamFinal, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this SynthesizedAudioStreamFinal to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for SynthesizedAudioStreamFinal
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** VoiceSessionState enum. */
        enum VoiceSessionState {
            VOICE_SESSION_STATE_UNSPECIFIED = 0,
            VOICE_SESSION_STATE_IDLE = 1,
            VOICE_SESSION_STATE_LISTENING = 2,
            VOICE_SESSION_STATE_USER_SPEAKING = 3,
            VOICE_SESSION_STATE_TRANSCRIBING = 4,
            VOICE_SESSION_STATE_THINKING = 5,
            VOICE_SESSION_STATE_SPEAKING = 6,
            VOICE_SESSION_STATE_INTERRUPTED = 7,
            VOICE_SESSION_STATE_CLOSED = 8,
            VOICE_SESSION_STATE_ERROR = 9
        }

        /** VoiceSessionEventKind enum. */
        enum VoiceSessionEventKind {
            VOICE_SESSION_EVENT_KIND_UNSPECIFIED = 0,
            VOICE_SESSION_EVENT_KIND_SESSION_STARTED = 1,
            VOICE_SESSION_EVENT_KIND_STATE_CHANGED = 2,
            VOICE_SESSION_EVENT_KIND_USER_TURN_STARTED = 3,
            VOICE_SESSION_EVENT_KIND_USER_TURN_FINALIZED = 4,
            VOICE_SESSION_EVENT_KIND_ASSISTANT_TURN_STARTED = 5,
            VOICE_SESSION_EVENT_KIND_ASSISTANT_TURN_COMPLETED = 6,
            VOICE_SESSION_EVENT_KIND_SESSION_CLOSED = 7,
            VOICE_SESSION_EVENT_KIND_ERROR = 8
        }

        /** Properties of a TurnIds. */
        interface ITurnIds {

            /** TurnIds sessionId */
            sessionId?: (string|null);

            /** TurnIds userTurnId */
            userTurnId?: (string|null);

            /** TurnIds assistantTurnId */
            assistantTurnId?: (string|null);
        }

        /** Represents a TurnIds. */
        class TurnIds implements ITurnIds {

            /**
             * Constructs a new TurnIds.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.ITurnIds);

            /** TurnIds sessionId. */
            public sessionId: string;

            /** TurnIds userTurnId. */
            public userTurnId: string;

            /** TurnIds assistantTurnId. */
            public assistantTurnId?: (string|null);

            /**
             * Creates a new TurnIds instance using the specified properties.
             * @param [properties] Properties to set
             * @returns TurnIds instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.ITurnIds): fluent_dialogue_dora.v1.TurnIds;

            /**
             * Encodes the specified TurnIds message. Does not implicitly {@link fluent_dialogue_dora.v1.TurnIds.verify|verify} messages.
             * @param message TurnIds message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.ITurnIds, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified TurnIds message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.TurnIds.verify|verify} messages.
             * @param message TurnIds message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.ITurnIds, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a TurnIds message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns TurnIds
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.TurnIds;

            /**
             * Decodes a TurnIds message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns TurnIds
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.TurnIds;

            /**
             * Verifies a TurnIds message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a TurnIds message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns TurnIds
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.TurnIds;

            /**
             * Creates a plain object from a TurnIds message. Also converts values to other types if specified.
             * @param message TurnIds
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.TurnIds, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this TurnIds to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for TurnIds
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a VoiceSessionEvent. */
        interface IVoiceSessionEvent {

            /** VoiceSessionEvent event */
            event?: (fluent_dialogue_dora.v1.VoiceSessionEventKind|null);

            /** VoiceSessionEvent state */
            state?: (fluent_dialogue_dora.v1.VoiceSessionState|null);

            /** VoiceSessionEvent seq */
            seq?: (number|Long|null);

            /** VoiceSessionEvent turnIds */
            turnIds?: (fluent_dialogue_dora.v1.ITurnIds|null);

            /** VoiceSessionEvent message */
            message?: (string|null);
        }

        /** Represents a VoiceSessionEvent. */
        class VoiceSessionEvent implements IVoiceSessionEvent {

            /**
             * Constructs a new VoiceSessionEvent.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IVoiceSessionEvent);

            /** VoiceSessionEvent event. */
            public event: fluent_dialogue_dora.v1.VoiceSessionEventKind;

            /** VoiceSessionEvent state. */
            public state: fluent_dialogue_dora.v1.VoiceSessionState;

            /** VoiceSessionEvent seq. */
            public seq: (number|Long);

            /** VoiceSessionEvent turnIds. */
            public turnIds?: (fluent_dialogue_dora.v1.ITurnIds|null);

            /** VoiceSessionEvent message. */
            public message?: (string|null);

            /**
             * Creates a new VoiceSessionEvent instance using the specified properties.
             * @param [properties] Properties to set
             * @returns VoiceSessionEvent instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IVoiceSessionEvent): fluent_dialogue_dora.v1.VoiceSessionEvent;

            /**
             * Encodes the specified VoiceSessionEvent message. Does not implicitly {@link fluent_dialogue_dora.v1.VoiceSessionEvent.verify|verify} messages.
             * @param message VoiceSessionEvent message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IVoiceSessionEvent, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified VoiceSessionEvent message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.VoiceSessionEvent.verify|verify} messages.
             * @param message VoiceSessionEvent message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IVoiceSessionEvent, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a VoiceSessionEvent message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns VoiceSessionEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.VoiceSessionEvent;

            /**
             * Decodes a VoiceSessionEvent message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns VoiceSessionEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.VoiceSessionEvent;

            /**
             * Verifies a VoiceSessionEvent message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a VoiceSessionEvent message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns VoiceSessionEvent
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.VoiceSessionEvent;

            /**
             * Creates a plain object from a VoiceSessionEvent message. Also converts values to other types if specified.
             * @param message VoiceSessionEvent
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.VoiceSessionEvent, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this VoiceSessionEvent to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for VoiceSessionEvent
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** PlaybackCommandKind enum. */
        enum PlaybackCommandKind {
            PLAYBACK_COMMAND_KIND_UNSPECIFIED = 0,
            PLAYBACK_COMMAND_KIND_STOP = 1,
            PLAYBACK_COMMAND_KIND_PAUSE = 2,
            PLAYBACK_COMMAND_KIND_RESUME = 3,
            PLAYBACK_COMMAND_KIND_CLEAR = 4
        }

        /** PlaybackStateKind enum. */
        enum PlaybackStateKind {
            PLAYBACK_STATE_KIND_UNSPECIFIED = 0,
            PLAYBACK_STATE_KIND_QUEUED = 1,
            PLAYBACK_STATE_KIND_PLAYING = 2,
            PLAYBACK_STATE_KIND_PAUSED = 3,
            PLAYBACK_STATE_KIND_STOPPED = 4,
            PLAYBACK_STATE_KIND_COMPLETED = 5,
            PLAYBACK_STATE_KIND_CANCELLED = 6,
            PLAYBACK_STATE_KIND_FAILED = 7
        }

        /** PlaybackDoneStatus enum. */
        enum PlaybackDoneStatus {
            PLAYBACK_DONE_STATUS_UNSPECIFIED = 0,
            PLAYBACK_DONE_STATUS_COMPLETED = 1,
            PLAYBACK_DONE_STATUS_STOPPED = 2,
            PLAYBACK_DONE_STATUS_CANCELLED = 3,
            PLAYBACK_DONE_STATUS_FAILED = 4
        }

        /** Properties of a PlaybackCommand. */
        interface IPlaybackCommand {

            /** PlaybackCommand command */
            command?: (fluent_dialogue_dora.v1.PlaybackCommandKind|null);

            /** PlaybackCommand requestId */
            requestId?: (string|null);

            /** PlaybackCommand streamId */
            streamId?: (string|null);

            /** PlaybackCommand seq */
            seq?: (number|Long|null);
        }

        /** Represents a PlaybackCommand. */
        class PlaybackCommand implements IPlaybackCommand {

            /**
             * Constructs a new PlaybackCommand.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IPlaybackCommand);

            /** PlaybackCommand command. */
            public command: fluent_dialogue_dora.v1.PlaybackCommandKind;

            /** PlaybackCommand requestId. */
            public requestId: string;

            /** PlaybackCommand streamId. */
            public streamId: string;

            /** PlaybackCommand seq. */
            public seq: (number|Long);

            /**
             * Creates a new PlaybackCommand instance using the specified properties.
             * @param [properties] Properties to set
             * @returns PlaybackCommand instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IPlaybackCommand): fluent_dialogue_dora.v1.PlaybackCommand;

            /**
             * Encodes the specified PlaybackCommand message. Does not implicitly {@link fluent_dialogue_dora.v1.PlaybackCommand.verify|verify} messages.
             * @param message PlaybackCommand message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IPlaybackCommand, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified PlaybackCommand message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.PlaybackCommand.verify|verify} messages.
             * @param message PlaybackCommand message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IPlaybackCommand, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a PlaybackCommand message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns PlaybackCommand
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.PlaybackCommand;

            /**
             * Decodes a PlaybackCommand message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns PlaybackCommand
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.PlaybackCommand;

            /**
             * Verifies a PlaybackCommand message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a PlaybackCommand message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns PlaybackCommand
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.PlaybackCommand;

            /**
             * Creates a plain object from a PlaybackCommand message. Also converts values to other types if specified.
             * @param message PlaybackCommand
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.PlaybackCommand, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this PlaybackCommand to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for PlaybackCommand
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** PlaybackControlKind enum. */
        enum PlaybackControlKind {
            PLAYBACK_CONTROL_KIND_UNSPECIFIED = 0,
            PLAYBACK_CONTROL_KIND_FLUSH = 1
        }

        /** Properties of a PlaybackControlCommand. */
        interface IPlaybackControlCommand {

            /** PlaybackControlCommand kind */
            kind?: (fluent_dialogue_dora.v1.PlaybackControlKind|null);

            /** PlaybackControlCommand streamId */
            streamId?: (string|null);

            /** PlaybackControlCommand seq */
            seq?: (number|Long|null);

            /** PlaybackControlCommand fadeOutMs */
            fadeOutMs?: (number|null);
        }

        /** Represents a PlaybackControlCommand. */
        class PlaybackControlCommand implements IPlaybackControlCommand {

            /**
             * Constructs a new PlaybackControlCommand.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IPlaybackControlCommand);

            /** PlaybackControlCommand kind. */
            public kind: fluent_dialogue_dora.v1.PlaybackControlKind;

            /** PlaybackControlCommand streamId. */
            public streamId: string;

            /** PlaybackControlCommand seq. */
            public seq: (number|Long);

            /** PlaybackControlCommand fadeOutMs. */
            public fadeOutMs: number;

            /**
             * Creates a new PlaybackControlCommand instance using the specified properties.
             * @param [properties] Properties to set
             * @returns PlaybackControlCommand instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IPlaybackControlCommand): fluent_dialogue_dora.v1.PlaybackControlCommand;

            /**
             * Encodes the specified PlaybackControlCommand message. Does not implicitly {@link fluent_dialogue_dora.v1.PlaybackControlCommand.verify|verify} messages.
             * @param message PlaybackControlCommand message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IPlaybackControlCommand, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified PlaybackControlCommand message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.PlaybackControlCommand.verify|verify} messages.
             * @param message PlaybackControlCommand message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IPlaybackControlCommand, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a PlaybackControlCommand message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns PlaybackControlCommand
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.PlaybackControlCommand;

            /**
             * Decodes a PlaybackControlCommand message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns PlaybackControlCommand
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.PlaybackControlCommand;

            /**
             * Verifies a PlaybackControlCommand message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a PlaybackControlCommand message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns PlaybackControlCommand
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.PlaybackControlCommand;

            /**
             * Creates a plain object from a PlaybackControlCommand message. Also converts values to other types if specified.
             * @param message PlaybackControlCommand
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.PlaybackControlCommand, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this PlaybackControlCommand to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for PlaybackControlCommand
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a PlaybackState. */
        interface IPlaybackState {

            /** PlaybackState requestId */
            requestId?: (string|null);

            /** PlaybackState sessionId */
            sessionId?: (string|null);

            /** PlaybackState userTurnId */
            userTurnId?: (string|null);

            /** PlaybackState streamId */
            streamId?: (string|null);

            /** PlaybackState state */
            state?: (fluent_dialogue_dora.v1.PlaybackStateKind|null);

            /** PlaybackState seq */
            seq?: (number|Long|null);

            /** PlaybackState playedFrames */
            playedFrames?: (number|Long|null);

            /** PlaybackState reason */
            reason?: (string|null);
        }

        /** Represents a PlaybackState. */
        class PlaybackState implements IPlaybackState {

            /**
             * Constructs a new PlaybackState.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IPlaybackState);

            /** PlaybackState requestId. */
            public requestId: string;

            /** PlaybackState sessionId. */
            public sessionId: string;

            /** PlaybackState userTurnId. */
            public userTurnId: string;

            /** PlaybackState streamId. */
            public streamId: string;

            /** PlaybackState state. */
            public state: fluent_dialogue_dora.v1.PlaybackStateKind;

            /** PlaybackState seq. */
            public seq: (number|Long);

            /** PlaybackState playedFrames. */
            public playedFrames: (number|Long);

            /** PlaybackState reason. */
            public reason?: (string|null);

            /**
             * Creates a new PlaybackState instance using the specified properties.
             * @param [properties] Properties to set
             * @returns PlaybackState instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IPlaybackState): fluent_dialogue_dora.v1.PlaybackState;

            /**
             * Encodes the specified PlaybackState message. Does not implicitly {@link fluent_dialogue_dora.v1.PlaybackState.verify|verify} messages.
             * @param message PlaybackState message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IPlaybackState, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified PlaybackState message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.PlaybackState.verify|verify} messages.
             * @param message PlaybackState message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IPlaybackState, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a PlaybackState message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns PlaybackState
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.PlaybackState;

            /**
             * Decodes a PlaybackState message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns PlaybackState
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.PlaybackState;

            /**
             * Verifies a PlaybackState message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a PlaybackState message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns PlaybackState
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.PlaybackState;

            /**
             * Creates a plain object from a PlaybackState message. Also converts values to other types if specified.
             * @param message PlaybackState
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.PlaybackState, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this PlaybackState to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for PlaybackState
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a PlaybackDone. */
        interface IPlaybackDone {

            /** PlaybackDone requestId */
            requestId?: (string|null);

            /** PlaybackDone sessionId */
            sessionId?: (string|null);

            /** PlaybackDone userTurnId */
            userTurnId?: (string|null);

            /** PlaybackDone streamId */
            streamId?: (string|null);

            /** PlaybackDone status */
            status?: (fluent_dialogue_dora.v1.PlaybackDoneStatus|null);

            /** PlaybackDone finalSequence */
            finalSequence?: (number|Long|null);

            /** PlaybackDone totalFrames */
            totalFrames?: (number|Long|null);

            /** PlaybackDone reason */
            reason?: (string|null);
        }

        /** Represents a PlaybackDone. */
        class PlaybackDone implements IPlaybackDone {

            /**
             * Constructs a new PlaybackDone.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IPlaybackDone);

            /** PlaybackDone requestId. */
            public requestId: string;

            /** PlaybackDone sessionId. */
            public sessionId: string;

            /** PlaybackDone userTurnId. */
            public userTurnId: string;

            /** PlaybackDone streamId. */
            public streamId: string;

            /** PlaybackDone status. */
            public status: fluent_dialogue_dora.v1.PlaybackDoneStatus;

            /** PlaybackDone finalSequence. */
            public finalSequence?: (number|Long|null);

            /** PlaybackDone totalFrames. */
            public totalFrames?: (number|Long|null);

            /** PlaybackDone reason. */
            public reason?: (string|null);

            /**
             * Creates a new PlaybackDone instance using the specified properties.
             * @param [properties] Properties to set
             * @returns PlaybackDone instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IPlaybackDone): fluent_dialogue_dora.v1.PlaybackDone;

            /**
             * Encodes the specified PlaybackDone message. Does not implicitly {@link fluent_dialogue_dora.v1.PlaybackDone.verify|verify} messages.
             * @param message PlaybackDone message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IPlaybackDone, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified PlaybackDone message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.PlaybackDone.verify|verify} messages.
             * @param message PlaybackDone message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IPlaybackDone, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a PlaybackDone message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns PlaybackDone
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.PlaybackDone;

            /**
             * Decodes a PlaybackDone message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns PlaybackDone
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.PlaybackDone;

            /**
             * Verifies a PlaybackDone message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a PlaybackDone message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns PlaybackDone
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.PlaybackDone;

            /**
             * Creates a plain object from a PlaybackDone message. Also converts values to other types if specified.
             * @param message PlaybackDone
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.PlaybackDone, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this PlaybackDone to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for PlaybackDone
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a BargeInEvent. */
        interface IBargeInEvent {

            /** BargeInEvent sessionId */
            sessionId?: (string|null);

            /** BargeInEvent sourceId */
            sourceId?: (string|null);

            /** BargeInEvent streamId */
            streamId?: (string|null);

            /** BargeInEvent seq */
            seq?: (number|Long|null);

            /** BargeInEvent playbackRequestId */
            playbackRequestId?: (string|null);

            /** BargeInEvent playbackStreamId */
            playbackStreamId?: (string|null);

            /** BargeInEvent playedFrames */
            playedFrames?: (number|Long|null);

            /** BargeInEvent detectedSampleIndex */
            detectedSampleIndex?: (number|Long|null);

            /** BargeInEvent speechProbability */
            speechProbability?: (number|null);
        }

        /** Represents a BargeInEvent. */
        class BargeInEvent implements IBargeInEvent {

            /**
             * Constructs a new BargeInEvent.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IBargeInEvent);

            /** BargeInEvent sessionId. */
            public sessionId: string;

            /** BargeInEvent sourceId. */
            public sourceId: string;

            /** BargeInEvent streamId. */
            public streamId: string;

            /** BargeInEvent seq. */
            public seq: (number|Long);

            /** BargeInEvent playbackRequestId. */
            public playbackRequestId: string;

            /** BargeInEvent playbackStreamId. */
            public playbackStreamId: string;

            /** BargeInEvent playedFrames. */
            public playedFrames: (number|Long);

            /** BargeInEvent detectedSampleIndex. */
            public detectedSampleIndex: (number|Long);

            /** BargeInEvent speechProbability. */
            public speechProbability: number;

            /**
             * Creates a new BargeInEvent instance using the specified properties.
             * @param [properties] Properties to set
             * @returns BargeInEvent instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IBargeInEvent): fluent_dialogue_dora.v1.BargeInEvent;

            /**
             * Encodes the specified BargeInEvent message. Does not implicitly {@link fluent_dialogue_dora.v1.BargeInEvent.verify|verify} messages.
             * @param message BargeInEvent message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IBargeInEvent, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified BargeInEvent message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.BargeInEvent.verify|verify} messages.
             * @param message BargeInEvent message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IBargeInEvent, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a BargeInEvent message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns BargeInEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.BargeInEvent;

            /**
             * Decodes a BargeInEvent message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns BargeInEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.BargeInEvent;

            /**
             * Verifies a BargeInEvent message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a BargeInEvent message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns BargeInEvent
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.BargeInEvent;

            /**
             * Creates a plain object from a BargeInEvent message. Also converts values to other types if specified.
             * @param message BargeInEvent
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.BargeInEvent, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this BargeInEvent to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for BargeInEvent
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a BargeInStreamFinal. */
        interface IBargeInStreamFinal {

            /** BargeInStreamFinal sessionId */
            sessionId?: (string|null);

            /** BargeInStreamFinal sourceId */
            sourceId?: (string|null);

            /** BargeInStreamFinal streamId */
            streamId?: (string|null);

            /** BargeInStreamFinal seq */
            seq?: (number|Long|null);
        }

        /** Represents a BargeInStreamFinal. */
        class BargeInStreamFinal implements IBargeInStreamFinal {

            /**
             * Constructs a new BargeInStreamFinal.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IBargeInStreamFinal);

            /** BargeInStreamFinal sessionId. */
            public sessionId: string;

            /** BargeInStreamFinal sourceId. */
            public sourceId: string;

            /** BargeInStreamFinal streamId. */
            public streamId: string;

            /** BargeInStreamFinal seq. */
            public seq: (number|Long);

            /**
             * Creates a new BargeInStreamFinal instance using the specified properties.
             * @param [properties] Properties to set
             * @returns BargeInStreamFinal instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IBargeInStreamFinal): fluent_dialogue_dora.v1.BargeInStreamFinal;

            /**
             * Encodes the specified BargeInStreamFinal message. Does not implicitly {@link fluent_dialogue_dora.v1.BargeInStreamFinal.verify|verify} messages.
             * @param message BargeInStreamFinal message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IBargeInStreamFinal, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified BargeInStreamFinal message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.BargeInStreamFinal.verify|verify} messages.
             * @param message BargeInStreamFinal message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IBargeInStreamFinal, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a BargeInStreamFinal message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns BargeInStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.BargeInStreamFinal;

            /**
             * Decodes a BargeInStreamFinal message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns BargeInStreamFinal
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.BargeInStreamFinal;

            /**
             * Verifies a BargeInStreamFinal message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a BargeInStreamFinal message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns BargeInStreamFinal
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.BargeInStreamFinal;

            /**
             * Creates a plain object from a BargeInStreamFinal message. Also converts values to other types if specified.
             * @param message BargeInStreamFinal
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.BargeInStreamFinal, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this BargeInStreamFinal to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for BargeInStreamFinal
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** DiagnosticSeverity enum. */
        enum DiagnosticSeverity {
            DIAGNOSTIC_SEVERITY_UNSPECIFIED = 0,
            DIAGNOSTIC_SEVERITY_OK = 1,
            DIAGNOSTIC_SEVERITY_WARN = 2,
            DIAGNOSTIC_SEVERITY_ERROR = 3,
            DIAGNOSTIC_SEVERITY_FATAL = 4
        }

        /** NodeState enum. */
        enum NodeState {
            NODE_STATE_UNSPECIFIED = 0,
            NODE_STATE_STARTING = 1,
            NODE_STATE_READY = 2,
            NODE_STATE_RUNNING = 3,
            NODE_STATE_DEGRADED = 4,
            NODE_STATE_STOPPING = 5,
            NODE_STATE_STOPPED = 6,
            NODE_STATE_FAILED = 7
        }

        /** Properties of a NodeStatus. */
        interface INodeStatus {

            /** NodeStatus nodeId */
            nodeId?: (string|null);

            /** NodeStatus state */
            state?: (fluent_dialogue_dora.v1.NodeState|null);

            /** NodeStatus seq */
            seq?: (number|Long|null);

            /** NodeStatus observedTimeNs */
            observedTimeNs?: (number|Long|null);

            /** NodeStatus message */
            message?: (string|null);
        }

        /** Represents a NodeStatus. */
        class NodeStatus implements INodeStatus {

            /**
             * Constructs a new NodeStatus.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.INodeStatus);

            /** NodeStatus nodeId. */
            public nodeId: string;

            /** NodeStatus state. */
            public state: fluent_dialogue_dora.v1.NodeState;

            /** NodeStatus seq. */
            public seq: (number|Long);

            /** NodeStatus observedTimeNs. */
            public observedTimeNs: (number|Long);

            /** NodeStatus message. */
            public message?: (string|null);

            /**
             * Creates a new NodeStatus instance using the specified properties.
             * @param [properties] Properties to set
             * @returns NodeStatus instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.INodeStatus): fluent_dialogue_dora.v1.NodeStatus;

            /**
             * Encodes the specified NodeStatus message. Does not implicitly {@link fluent_dialogue_dora.v1.NodeStatus.verify|verify} messages.
             * @param message NodeStatus message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.INodeStatus, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified NodeStatus message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.NodeStatus.verify|verify} messages.
             * @param message NodeStatus message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.INodeStatus, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a NodeStatus message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns NodeStatus
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.NodeStatus;

            /**
             * Decodes a NodeStatus message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns NodeStatus
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.NodeStatus;

            /**
             * Verifies a NodeStatus message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a NodeStatus message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns NodeStatus
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.NodeStatus;

            /**
             * Creates a plain object from a NodeStatus message. Also converts values to other types if specified.
             * @param message NodeStatus
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.NodeStatus, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this NodeStatus to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for NodeStatus
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a DiagnosticEvent. */
        interface IDiagnosticEvent {

            /** DiagnosticEvent nodeId */
            nodeId?: (string|null);

            /** DiagnosticEvent severity */
            severity?: (fluent_dialogue_dora.v1.DiagnosticSeverity|null);

            /** DiagnosticEvent seq */
            seq?: (number|Long|null);

            /** DiagnosticEvent observedTimeNs */
            observedTimeNs?: (number|Long|null);

            /** DiagnosticEvent code */
            code?: (string|null);

            /** DiagnosticEvent message */
            message?: (string|null);
        }

        /** Represents a DiagnosticEvent. */
        class DiagnosticEvent implements IDiagnosticEvent {

            /**
             * Constructs a new DiagnosticEvent.
             * @param [properties] Properties to set
             */
            constructor(properties?: fluent_dialogue_dora.v1.IDiagnosticEvent);

            /** DiagnosticEvent nodeId. */
            public nodeId: string;

            /** DiagnosticEvent severity. */
            public severity: fluent_dialogue_dora.v1.DiagnosticSeverity;

            /** DiagnosticEvent seq. */
            public seq: (number|Long);

            /** DiagnosticEvent observedTimeNs. */
            public observedTimeNs: (number|Long);

            /** DiagnosticEvent code. */
            public code: string;

            /** DiagnosticEvent message. */
            public message: string;

            /**
             * Creates a new DiagnosticEvent instance using the specified properties.
             * @param [properties] Properties to set
             * @returns DiagnosticEvent instance
             */
            public static create(properties?: fluent_dialogue_dora.v1.IDiagnosticEvent): fluent_dialogue_dora.v1.DiagnosticEvent;

            /**
             * Encodes the specified DiagnosticEvent message. Does not implicitly {@link fluent_dialogue_dora.v1.DiagnosticEvent.verify|verify} messages.
             * @param message DiagnosticEvent message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: fluent_dialogue_dora.v1.IDiagnosticEvent, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified DiagnosticEvent message, length delimited. Does not implicitly {@link fluent_dialogue_dora.v1.DiagnosticEvent.verify|verify} messages.
             * @param message DiagnosticEvent message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: fluent_dialogue_dora.v1.IDiagnosticEvent, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a DiagnosticEvent message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns DiagnosticEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): fluent_dialogue_dora.v1.DiagnosticEvent;

            /**
             * Decodes a DiagnosticEvent message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns DiagnosticEvent
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): fluent_dialogue_dora.v1.DiagnosticEvent;

            /**
             * Verifies a DiagnosticEvent message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a DiagnosticEvent message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns DiagnosticEvent
             */
            public static fromObject(object: { [k: string]: any }): fluent_dialogue_dora.v1.DiagnosticEvent;

            /**
             * Creates a plain object from a DiagnosticEvent message. Also converts values to other types if specified.
             * @param message DiagnosticEvent
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: fluent_dialogue_dora.v1.DiagnosticEvent, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this DiagnosticEvent to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for DiagnosticEvent
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }
    }
}

/** Namespace google. */
export namespace google {

    /** Namespace protobuf. */
    namespace protobuf {

        /** Properties of a Struct. */
        interface IStruct {

            /** Struct fields */
            fields?: ({ [k: string]: google.protobuf.IValue }|null);
        }

        /** Represents a Struct. */
        class Struct implements IStruct {

            /**
             * Constructs a new Struct.
             * @param [properties] Properties to set
             */
            constructor(properties?: google.protobuf.IStruct);

            /** Struct fields. */
            public fields: { [k: string]: google.protobuf.IValue };

            /**
             * Creates a new Struct instance using the specified properties.
             * @param [properties] Properties to set
             * @returns Struct instance
             */
            public static create(properties?: google.protobuf.IStruct): google.protobuf.Struct;

            /**
             * Encodes the specified Struct message. Does not implicitly {@link google.protobuf.Struct.verify|verify} messages.
             * @param message Struct message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: google.protobuf.IStruct, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified Struct message, length delimited. Does not implicitly {@link google.protobuf.Struct.verify|verify} messages.
             * @param message Struct message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: google.protobuf.IStruct, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a Struct message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns Struct
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): google.protobuf.Struct;

            /**
             * Decodes a Struct message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns Struct
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): google.protobuf.Struct;

            /**
             * Verifies a Struct message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a Struct message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns Struct
             */
            public static fromObject(object: { [k: string]: any }): google.protobuf.Struct;

            /**
             * Creates a plain object from a Struct message. Also converts values to other types if specified.
             * @param message Struct
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: google.protobuf.Struct, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this Struct to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for Struct
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** Properties of a Value. */
        interface IValue {

            /** Value nullValue */
            nullValue?: (google.protobuf.NullValue|null);

            /** Value numberValue */
            numberValue?: (number|null);

            /** Value stringValue */
            stringValue?: (string|null);

            /** Value boolValue */
            boolValue?: (boolean|null);

            /** Value structValue */
            structValue?: (google.protobuf.IStruct|null);

            /** Value listValue */
            listValue?: (google.protobuf.IListValue|null);
        }

        /** Represents a Value. */
        class Value implements IValue {

            /**
             * Constructs a new Value.
             * @param [properties] Properties to set
             */
            constructor(properties?: google.protobuf.IValue);

            /** Value nullValue. */
            public nullValue?: (google.protobuf.NullValue|null);

            /** Value numberValue. */
            public numberValue?: (number|null);

            /** Value stringValue. */
            public stringValue?: (string|null);

            /** Value boolValue. */
            public boolValue?: (boolean|null);

            /** Value structValue. */
            public structValue?: (google.protobuf.IStruct|null);

            /** Value listValue. */
            public listValue?: (google.protobuf.IListValue|null);

            /** Value kind. */
            public kind?: ("nullValue"|"numberValue"|"stringValue"|"boolValue"|"structValue"|"listValue");

            /**
             * Creates a new Value instance using the specified properties.
             * @param [properties] Properties to set
             * @returns Value instance
             */
            public static create(properties?: google.protobuf.IValue): google.protobuf.Value;

            /**
             * Encodes the specified Value message. Does not implicitly {@link google.protobuf.Value.verify|verify} messages.
             * @param message Value message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: google.protobuf.IValue, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified Value message, length delimited. Does not implicitly {@link google.protobuf.Value.verify|verify} messages.
             * @param message Value message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: google.protobuf.IValue, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a Value message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns Value
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): google.protobuf.Value;

            /**
             * Decodes a Value message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns Value
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): google.protobuf.Value;

            /**
             * Verifies a Value message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a Value message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns Value
             */
            public static fromObject(object: { [k: string]: any }): google.protobuf.Value;

            /**
             * Creates a plain object from a Value message. Also converts values to other types if specified.
             * @param message Value
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: google.protobuf.Value, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this Value to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for Value
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }

        /** NullValue enum. */
        enum NullValue {
            NULL_VALUE = 0
        }

        /** Properties of a ListValue. */
        interface IListValue {

            /** ListValue values */
            values?: (google.protobuf.IValue[]|null);
        }

        /** Represents a ListValue. */
        class ListValue implements IListValue {

            /**
             * Constructs a new ListValue.
             * @param [properties] Properties to set
             */
            constructor(properties?: google.protobuf.IListValue);

            /** ListValue values. */
            public values: google.protobuf.IValue[];

            /**
             * Creates a new ListValue instance using the specified properties.
             * @param [properties] Properties to set
             * @returns ListValue instance
             */
            public static create(properties?: google.protobuf.IListValue): google.protobuf.ListValue;

            /**
             * Encodes the specified ListValue message. Does not implicitly {@link google.protobuf.ListValue.verify|verify} messages.
             * @param message ListValue message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encode(message: google.protobuf.IListValue, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified ListValue message, length delimited. Does not implicitly {@link google.protobuf.ListValue.verify|verify} messages.
             * @param message ListValue message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            public static encodeDelimited(message: google.protobuf.IListValue, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a ListValue message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns ListValue
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): google.protobuf.ListValue;

            /**
             * Decodes a ListValue message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns ListValue
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            public static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): google.protobuf.ListValue;

            /**
             * Verifies a ListValue message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            public static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a ListValue message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns ListValue
             */
            public static fromObject(object: { [k: string]: any }): google.protobuf.ListValue;

            /**
             * Creates a plain object from a ListValue message. Also converts values to other types if specified.
             * @param message ListValue
             * @param [options] Conversion options
             * @returns Plain object
             */
            public static toObject(message: google.protobuf.ListValue, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this ListValue to JSON.
             * @returns JSON object
             */
            public toJSON(): { [k: string]: any };

            /**
             * Gets the default type url for ListValue
             * @param [typeUrlPrefix] your custom typeUrlPrefix(default "type.googleapis.com")
             * @returns The default type url
             */
            public static getTypeUrl(typeUrlPrefix?: string): string;
        }
    }
}
