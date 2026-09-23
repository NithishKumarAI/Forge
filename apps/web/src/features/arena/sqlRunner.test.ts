import {afterEach,describe,expect,it,vi} from "vitest";
import {runSql} from "./sqlRunner";

class FakeWorker {
  static instances:FakeWorker[]=[];
  onmessage:((event:{data:unknown})=>void)|null=null;
  onerror:(()=>void)|null=null;
  terminated=false;
  constructor(){FakeWorker.instances.push(this)}
  postMessage(message:{id:number}){queueMicrotask(()=>this.onmessage?.({data:{id:message.id,ok:true,columns:["value"],rows:[{value:1}],duration_ms:1}}))}
  terminate(){this.terminated=true}
}

afterEach(()=>{FakeWorker.instances=[];vi.unstubAllGlobals();vi.useRealTimers()});
describe("isolated SQL runner",()=>{
  it("creates and discards a fresh worker/database for every run",async()=>{vi.stubGlobal("Worker",FakeWorker);const first=await runSql("CREATE TABLE x(value int)","SELECT 1");const second=await runSql("CREATE TABLE x(value int)","SELECT 1");expect(first.ok&&second.ok).toBe(true);expect(FakeWorker.instances).toHaveLength(2);expect(FakeWorker.instances.every(worker=>worker.terminated)).toBe(true)});
  it("terminates a timed-out worker and recovers on the next run",async()=>{class TimeoutWorker extends FakeWorker{override postMessage(){/* intentionally hangs */}}vi.useFakeTimers();vi.stubGlobal("Worker",TimeoutWorker);const pending=runSql("","",10);await vi.advanceTimersByTimeAsync(11);expect((await pending).errorCategory).toBe("Timeout");vi.useRealTimers();vi.stubGlobal("Worker",FakeWorker);expect((await runSql("","",100)).ok).toBe(true)});
});
