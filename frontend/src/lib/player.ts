const MP3_URL = 'https://bstrama.com/files/learn-en-mp3/';

export interface ContentInfo {
    fileName: string;
    en: string;
    pl: string;
}

export type Status = 'PLAYING' | 'PAUSED' | 'LOADING';

export class Player {
    private readonly book: string;
    private readonly chapter: string;
    private audio: HTMLAudioElement;
    private nextAudio: HTMLAudioElement;
    private volume: number = 1;
    private onNewIndex: (() => void)[] = [];
    private onNewStatus: (() => void)[] = [];

    public readonly contentInfo: ContentInfo[];
    public nextContentIndex: number = 0;
    private _status: Status = 'PAUSED';
   
    public set status(status: Status) {
        this._status = status;
        this.onNewStatus.forEach(cb => cb());
    }

    public get status(): Status {
        return this._status;
    }

    private constructor(book: string, chapter: string, contentInfo: ContentInfo[]) {
        this.book = book;
        this.chapter = chapter;
        this.contentInfo = contentInfo;
        this.audio = new Audio();
        this.nextAudio = new Audio(`${MP3_URL}${book}/${chapter}/0.mp3`);

        this.nextAudio.load();
        this.next().catch(console.error);
    }

    public get playlistLength(): number {
        return this.contentInfo.length;
    }

    public setVolume(volume: number): void {
        this.volume = volume;
        this.audio.volume = this.volume;
        this.nextAudio.volume = this.volume;
    }

    public onCurrentIndexChange(callback: (index: number) => void): void {
        this.onNewIndex.push(() => {
            callback((this.nextContentIndex - 1 + this.contentInfo.length) % this.contentInfo.length);
        });
    }
    
    public onStatusChange(callback: (status: Status) => void): void {
        this.onNewStatus.push(() => {
            callback(this.status);
        });
    }

    public destroy(): void {
        this.audio.pause();
        this.audio.remove();
        this.nextAudio.pause();
        this.nextAudio.remove();
    }

    public async play(): Promise<void> {
        if (this.audio.paused) {
            this.status = 'LOADING';
            await this.audio.play();
        }
        this.status = 'PLAYING';
    }

    public pause(): void {
        this.audio.pause();
        this.status = 'PAUSED';
    }

    public async setCurrentIndex(index: number, timeIntervalBeforePlayMs: number = 300): Promise<void> {
        if (index === this.nextContentIndex-1) return;
        
        this.nextContentIndex = index;
        this.nextAudio = new Audio(`${MP3_URL}${this.book}/${this.chapter}/${this.nextContentIndex}.mp3`);
        this.nextAudio.load();
        this.nextAudio.volume = this.volume;

        await this.next(timeIntervalBeforePlayMs);
    }

    public async prev(timeIntervalBeforePlayMs: number = 0): Promise<void> {
        this.nextContentIndex = (this.nextContentIndex - 3 + this.contentInfo.length) % this.contentInfo.length;

        await this.next();
        await this.next(timeIntervalBeforePlayMs);
    }

    public async next(timeIntervalBeforePlayMs: number = 0): Promise<void> {
        this.audio.pause();
        this.audio.remove();
        this.audio = this.nextAudio;
        this.nextContentIndex = (this.nextContentIndex + 1) % this.contentInfo.length;
        this.nextAudio = new Audio(`${MP3_URL}${this.book}/${this.chapter}/${this.nextContentIndex}.mp3`);
        this.nextAudio.load();
        this.nextAudio.volume = this.volume;
        
        this.onNewIndex.forEach(cb => cb());

        if (this.status !== 'PAUSED') {
            await new Promise(resolve => setTimeout(resolve, timeIntervalBeforePlayMs));
            await this.play();
        }

        this.audio.addEventListener('ended', async () => {
            await this.next();
        });

        this.audio.addEventListener('error', () => {
            this.status = 'PAUSED';
        });
    }

    static async create(book: string, chapter: string): Promise<Player> {
        const contentInfo: ContentInfo[] = await fetch(`${MP3_URL}${book}/${chapter}/content.json`)
            .then(res => res.json())
            .then(rawRes => {
                const result: ContentInfo[] = [];
                Object.keys(rawRes)
                    // all keys are '0.mp3', '1.mp3', '2.mp3', etc.
                    .toSorted((a, b) => parseInt(a) - parseInt(b))
                    .forEach((key, index) => {
                        result.push({
                            ...rawRes[key],
                            fileName: `${index}.mp3`
                        });
                    });

                return result;
            });

        return new Player(book, chapter, contentInfo);
    }
}