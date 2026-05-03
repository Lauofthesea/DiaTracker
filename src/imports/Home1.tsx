import svgPaths from "./svg-2sgjqsqskz";
import imgContainer from "figma:asset/f7433eaa187b6e62ecc358d9e754c05d7eca41c3.png";
import imgImage from "figma:asset/4954dae4d7c125e866348aa3419a3d4a2322972c.png";

function Container1() {
  return (
    <div className="absolute left-0 size-[16px] top-[2px]" data-name="Container">
      <svg className="absolute block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 16 16">
        <g id="Container">
          <path clipRule="evenodd" d={svgPaths.p1683c330} fill="var(--fill-0, #F59E0B)" fillRule="evenodd" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function Container() {
  return (
    <div className="absolute h-[20px] left-[20px] top-[20px] w-[142px]" data-name="Container">
      <Container1 />
      <p className="absolute font-['Geist:Medium',sans-serif] font-medium h-[20px] leading-[20px] left-[23px] text-[#637c84] text-[14px] top-0 w-[56px]" style={{ fontFeatureSettings: "'dlig'" }}>
        Calories
      </p>
    </div>
  );
}

function Container2() {
  return (
    <div className="absolute h-[20px] left-[20px] top-[168px] w-[142px]" data-name="Container">
      <p className="-translate-x-1/2 absolute font-['Nunito_Sans:Medium',sans-serif] font-medium h-[20px] leading-[20px] left-[70.91px] text-[#1e6177] text-[14px] text-center top-0 w-[94px]" style={{ fontVariationSettings: "'YTLC' 500, 'wdth' 100", fontFeatureSettings: "'dlig'" }}>
        550 remaining
      </p>
    </div>
  );
}

function Container3() {
  return (
    <div className="absolute left-0 size-[96px] top-0" data-name="Container">
      <svg className="absolute block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 96 96">
        <g clipPath="url(#clip0_1_187)" id="Container">
          <path clipRule="evenodd" d={svgPaths.p27718c80} fillRule="evenodd" id="Vector" stroke="var(--stroke-0, #E2EAEB)" strokeWidth="10.6667" />
          <g id="Vector_2" />
        </g>
        <defs>
          <clipPath id="clip0_1_187">
            <rect fill="white" height="96" width="96" />
          </clipPath>
        </defs>
      </svg>
    </div>
  );
}

function Container5() {
  return (
    <div className="absolute h-[28px] left-[24.73px] top-[26.5px] w-[47px]" data-name="Container">
      <p className="absolute font-['Geist:Bold',sans-serif] font-bold h-[24px] leading-[28px] left-[-1.5px] text-[#0d2b35] text-[18px] top-[1.6px] tracking-[-0.45px] w-[50px]" style={{ fontFeatureSettings: "'dlig'" }}>
        1,450
      </p>
    </div>
  );
}

function Container6() {
  return (
    <div className="absolute h-[15px] left-[31.7px] top-[54.5px] w-[33px]" data-name="Container">
      <p className="absolute font-['Nunito_Sans:SemiBold',sans-serif] font-semibold h-[14px] leading-[15px] left-[-1px] text-[#637c84] text-[10px] top-0 tracking-[0.5px] uppercase w-[35px]" style={{ fontVariationSettings: "'YTLC' 500, 'wdth' 100", fontFeatureSettings: "'dlig'" }}>
        / 2000
      </p>
    </div>
  );
}

function Container4() {
  return (
    <div className="absolute left-0 size-[96px] top-0" data-name="Container">
      <Container5 />
      <Container6 />
      <div className="-translate-y-1/2 absolute h-[84.883px] left-[6.67%] right-[21.98%] top-[calc(50%+0.9px)]" data-name="Vector">
        <div className="absolute inset-[-6.28%_-5.47%_-6.28%_-7.79%]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 77.5805 95.5493">
            <path d={svgPaths.p2e679e0} id="Vector" stroke="var(--stroke-0, #3ADE3F)" strokeWidth="10.6667" />
          </svg>
        </div>
      </div>
    </div>
  );
}

function Caltrack() {
  return (
    <div className="absolute left-[42.8px] size-[96px] top-[56px]" data-name="caltrack">
      <Container3 />
      <Container4 />
    </div>
  );
}

function Calorie() {
  return (
    <div className="absolute bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] border-solid h-[210px] left-0 rounded-[16px] shadow-[0px_4px_24px_0px_rgba(13,43,53,0.06)] top-0 w-[184px]" data-name="calorie">
      <Container />
      <Container2 />
      <Caltrack />
    </div>
  );
}

function Container8() {
  return (
    <div className="absolute left-0 size-[16px] top-[2px]" data-name="Container">
      <svg className="absolute block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 16 16">
        <g id="Container">
          <path clipRule="evenodd" d={svgPaths.pea08000} fill="var(--fill-0, #FCD34D)" fillRule="evenodd" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function Container7() {
  return (
    <div className="absolute h-[20px] left-[20px] top-[20px] w-[142px]" data-name="Container">
      <Container8 />
      <p className="absolute font-['Geist:Medium',sans-serif] font-medium h-[20px] leading-[20px] left-[23px] text-[#637c84] text-[14px] top-0 w-[41px]" style={{ fontFeatureSettings: "'dlig'" }}>
        Carbs
      </p>
    </div>
  );
}

function Container9() {
  return (
    <div className="absolute h-[20px] left-[20px] top-[168px] w-[142px]" data-name="Container">
      <p className="-translate-x-1/2 absolute font-['Nunito_Sans:Medium',sans-serif] font-medium h-[20px] leading-[20px] left-[71.01px] text-[#f59e0b] text-[14px] text-center top-0 w-[84px]" style={{ fontVariationSettings: "'YTLC' 500, 'wdth' 100", fontFeatureSettings: "'dlig'" }}>
        Nearing limit
      </p>
    </div>
  );
}

function Container11() {
  return (
    <div className="absolute left-0 size-[96px] top-0" data-name="Container">
      <svg className="absolute block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 96 96">
        <g clipPath="url(#clip0_1_207)" id="Container">
          <path clipRule="evenodd" d={svgPaths.p6715800} fillRule="evenodd" id="Vector" stroke="var(--stroke-0, #E2EAEB)" strokeWidth="10.6667" />
          <path d={svgPaths.p1eb10c00} id="Vector_2" stroke="var(--stroke-0, #FFEE57)" strokeLinecap="round" strokeWidth="10.6667" />
        </g>
        <defs>
          <clipPath id="clip0_1_207">
            <rect fill="white" height="96" width="96" />
          </clipPath>
        </defs>
      </svg>
    </div>
  );
}

function Container12() {
  return (
    <div className="absolute h-[28px] left-[26.96px] top-[26.5px] w-[43px]" data-name="Container">
      <p className="absolute font-['Geist:Bold',sans-serif] font-bold h-[24px] leading-[28px] left-[-1.5px] text-[#0d2b35] text-[18px] top-[1.6px] tracking-[-0.45px] w-[46px]" style={{ fontFeatureSettings: "'dlig'" }}>
        180g
      </p>
    </div>
  );
}

function Container13() {
  return (
    <div className="absolute h-[15px] left-[31.04px] top-[54.5px] w-[34px]" data-name="Container">
      <p className="absolute font-['Nunito_Sans:SemiBold',sans-serif] font-semibold h-[14px] leading-[15px] left-[-1px] text-[#637c84] text-[10px] top-0 tracking-[0.5px] uppercase w-[36px]" style={{ fontVariationSettings: "'YTLC' 500, 'wdth' 100", fontFeatureSettings: "'dlig'" }}>
        / 220g
      </p>
    </div>
  );
}

function Carbtrack() {
  return (
    <div className="absolute left-0 size-[96px] top-0" data-name="carbtrack">
      <Container12 />
      <Container13 />
    </div>
  );
}

function Container10() {
  return (
    <div className="absolute left-[42.8px] size-[96px] top-[56px]" data-name="Container">
      <Container11 />
      <Carbtrack />
    </div>
  );
}

function Carbs() {
  return (
    <div className="absolute bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] border-solid h-[210px] left-[199.2px] rounded-[16px] shadow-[0px_4px_24px_0px_rgba(13,43,53,0.06)] top-0 w-[184px]" data-name="carbs">
      <Container7 />
      <Container9 />
      <Container10 />
    </div>
  );
}

function Data() {
  return (
    <div className="absolute h-[210px] left-[24px] top-[567.74px] w-[383px]" data-name="data">
      <Calorie />
      <Carbs />
    </div>
  );
}

function Container14() {
  return (
    <div className="absolute left-[115.56px] size-[24px] top-[18px]" data-name="Container">
      <svg className="absolute block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="Container">
          <path clipRule="evenodd" d={svgPaths.p2e182800} fill="var(--fill-0, white)" fillRule="evenodd" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function AddMeal() {
  return (
    <div className="absolute bg-[#1e6177] h-[60px] left-[24px] rounded-[26843500px] shadow-[0px_4px_6px_0px_rgba(30,97,119,0.25),0px_10px_15px_0px_rgba(30,97,119,0.25)] top-[809.34px] w-[383px]" data-name="add-meal">
      <Container14 />
      <p className="-translate-x-1/2 absolute font-['Geist:Medium',sans-serif] font-medium h-[28px] leading-[28px] left-[207.56px] text-[18px] text-center text-white top-[16px] w-[122px]" style={{ fontFeatureSettings: "'dlig'" }}>
        Log New Meal
      </p>
    </div>
  );
}

function Container15() {
  return <div className="absolute bg-[rgba(245,158,11,0.1)] blur-[32px] right-[-39.4px] rounded-[26843500px] size-[160px] top-[-40px]" data-name="Container" />;
}

function Container17() {
  return (
    <div className="absolute left-[10px] size-[20px] top-[10px]" data-name="Container">
      <svg className="absolute block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 20 20">
        <g id="Container">
          <path clipRule="evenodd" d={svgPaths.pb74cd00} fill="var(--fill-0, #92400E)" fillRule="evenodd" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function Container16() {
  return (
    <div className="absolute bg-[#fef3c7] left-[5px] rounded-[26843500px] shadow-[0px_1px_2px_0px_rgba(0,0,0,0.1),0px_1px_3px_0px_rgba(0,0,0,0.1)] size-[40px] top-[11.5px]" data-name="Container">
      <Container17 />
    </div>
  );
}

function Container18() {
  return (
    <div className="absolute h-[33px] left-[56.2px] top-[10.4px] w-[325px]" data-name="Container">
      <p className="absolute font-['Geist:SemiBold',sans-serif] font-semibold h-[21px] leading-[24px] left-[-1px] text-[#92400e] text-[16px] top-[1.6px] tracking-[-0.4px] w-[131px]" style={{ fontFeatureSettings: "'dlig'" }}>
        Attention Needed
      </p>
    </div>
  );
}

function Container19() {
  return (
    <div className="absolute h-[69px] left-[56px] top-[40.5px] w-[325px]" data-name="Container">
      <p className="absolute font-['Nunito_Sans:Regular',sans-serif] font-normal h-[65px] leading-[22.75px] left-[-1px] text-[14px] text-[rgba(146,64,14,0.8)] top-[1.6px] w-[320px]" style={{ fontVariationSettings: "'YTLC' 500, 'wdth' 100", fontFeatureSettings: "'dlig'" }}>
        Your predicted glucose indicates a moderate risk of hyperglycemia following your last logged meal. Consider a 15-minute walk.
      </p>
    </div>
  );
}

function NoteNotif() {
  return (
    <div className="absolute bg-[rgba(254,243,199,0.4)] border-[0.8px] border-[rgba(254,243,199,0.2)] border-solid h-[118px] left-[24px] overflow-clip rounded-[16px] shadow-[0px_1px_2px_-1px_rgba(0,0,0,0.1),0px_1px_3px_0px_rgba(0,0,0,0.1)] top-[104.8px] w-[383px]" data-name="note-notif">
      <Container15 />
      <Container16 />
      <Container18 />
      <Container19 />
    </div>
  );
}

function StatusTab() {
  return <div className="absolute bg-gradient-to-b from-[rgba(138,171,159,0.05)] h-[280px] right-[24.2px] to-[rgba(138,171,159,0)] top-[255.8px] w-[381px]" data-name="status-tab" />;
}

function GlcStat() {
  return (
    <div className="absolute h-[28px] left-0 top-0 w-[154px]" data-name="glc-stat">
      <p className="absolute font-['Geist:SemiBold',sans-serif] font-semibold h-[28px] leading-[28px] left-[27px] text-[#0d2b35] text-[18px] top-0 tracking-[-0.45px] w-[128px]" style={{ fontFeatureSettings: "'dlig'" }}>
        Glucose Status
      </p>
    </div>
  );
}

function StatusId() {
  return (
    <div className="absolute bg-[rgba(86,70,70,0.1)] h-[24px] left-[258.11px] rounded-[26843500px] top-[2px] w-[75px]" data-name="status-id">
      <p className="absolute font-['Nunito_Sans:SemiBold',sans-serif] font-semibold h-[16px] leading-[16px] left-[11px] text-[#179b6b] text-[12px] top-[4px] tracking-[0.3px] w-[53px]" style={{ fontVariationSettings: "'YTLC' 500, 'wdth' 100", fontFeatureSettings: "'dlig'" }}>
        In Range
      </p>
    </div>
  );
}

function Container21() {
  return (
    <div className="absolute left-[-10.8px] rounded-[26843500px] shadow-[0px_1px_2px_0px_rgba(0,0,0,0.1),0px_1px_3px_0px_rgba(0,0,0,0.1)] size-[32px] top-[-1.8px]" data-name="Container">
      <img alt="" className="absolute inset-0 max-w-none object-cover pointer-events-none rounded-[26843500px] size-full" src={imgContainer} />
    </div>
  );
}

function Container20() {
  return (
    <div className="absolute h-[28px] left-[48.8px] top-[279.8px] w-[333px]" data-name="Container">
      <GlcStat />
      <StatusId />
      <Container21 />
    </div>
  );
}

function Container24() {
  return (
    <div className="absolute h-[20px] left-0 top-0 w-[130px]" data-name="Container">
      <p className="absolute font-['Nunito_Sans:Medium',sans-serif] font-medium h-[20px] leading-[20px] left-[-1px] text-[#637c84] text-[14px] top-0 w-[109px]" style={{ fontVariationSettings: "'YTLC' 500, 'wdth' 100", fontFeatureSettings: "'dlig'" }}>
        Current Estimate
      </p>
    </div>
  );
}

function Container26() {
  return (
    <div className="absolute h-[48px] left-0 top-0 w-[79px]" data-name="Container">
      <p className="absolute font-['Geist:Bold',sans-serif] font-bold h-[63px] leading-[48px] left-[-1.5px] text-[#0d2b35] text-[48px] top-0 tracking-[-2.4px] w-[82px]" style={{ fontFeatureSettings: "'dlig'" }}>
        104
      </p>
    </div>
  );
}

function Container27() {
  return (
    <div className="absolute h-[24px] left-[84.63px] top-[24px] w-[46px]" data-name="Container">
      <p className="absolute font-['Nunito_Sans:Medium',sans-serif] font-medium h-[22px] leading-[24px] left-[-1px] text-[#637c84] text-[16px] top-[0.8px] w-[48px]" style={{ fontVariationSettings: "'YTLC' 500, 'wdth' 100", fontFeatureSettings: "'dlig'" }}>
        mg/dL
      </p>
    </div>
  );
}

function Container25() {
  return (
    <div className="absolute h-[48px] left-0 top-[24px] w-[130px]" data-name="Container">
      <Container26 />
      <Container27 />
    </div>
  );
}

function Container23() {
  return (
    <div className="absolute h-[72px] left-0 top-0 w-[130px]" data-name="Container">
      <Container24 />
      <Container25 />
    </div>
  );
}

function Container30() {
  return <div className="absolute bg-[rgba(226,234,235,0.4)] h-[15px] left-0 rounded-tl-[12px] rounded-tr-[12px] top-[33.6px] w-[25px]" data-name="Container" />;
}

function Container31() {
  return <div className="absolute bg-[rgba(226,234,235,0.5)] h-[20px] left-[30.86px] rounded-tl-[12px] rounded-tr-[12px] top-[28.8px] w-[25px]" data-name="Container" />;
}

function Container32() {
  return <div className="absolute bg-[rgba(226,234,235,0.6)] h-[29px] left-[61.71px] rounded-tl-[12px] rounded-tr-[12px] top-[19.2px] w-[25px]" data-name="Container" />;
}

function Container33() {
  return <div className="absolute bg-[rgba(138,171,159,0.4)] h-[39px] left-[92.56px] rounded-tl-[12px] rounded-tr-[12px] top-[9.6px] w-[25px]" data-name="Container" />;
}

function Container34() {
  return <div className="absolute bg-[rgba(254,243,199,0.4)] h-[46px] left-[154.26px] rounded-tl-[12px] rounded-tr-[12px] top-[2.4px] w-[25px]" data-name="Container" />;
}

function Container36() {
  return <div className="absolute bg-[#8aab9f] right-[9.57px] rounded-[26843500px] shadow-[0px_0px_8px_0px_rgba(138,171,159,0.8)] size-[6px] top-[-6px]" data-name="Container" />;
}

function Container35() {
  return (
    <div className="absolute bg-[rgba(138,171,159,0.6)] h-[41px] left-[123.41px] rounded-tl-[12px] rounded-tr-[12px] top-[7.2px] w-[25px]" data-name="Container">
      <Container36 />
    </div>
  );
}

function Container29() {
  return (
    <div className="absolute h-[48px] left-0 top-0 w-[180px]" data-name="Container">
      <Container30 />
      <Container31 />
      <Container32 />
      <Container33 />
      <Container34 />
      <Container35 />
    </div>
  );
}

function Container28() {
  return (
    <div className="absolute h-[52px] left-[153.69px] top-[20px] w-[180px]" data-name="Container">
      <Container29 />
    </div>
  );
}

function Container22() {
  return (
    <div className="absolute h-[72px] left-[48.8px] top-[331.8px] w-[333px]" data-name="Container">
      <Container23 />
      <Container28 />
    </div>
  );
}

function G() {
  return (
    <div className="absolute inset-[8.33%]" data-name="g">
      <div className="absolute inset-[-3.75%]">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 14.3333 14.3333">
          <g id="g">
            <path clipRule="evenodd" d={svgPaths.p3a182a00} fillRule="evenodd" id="Vector" stroke="var(--stroke-0, #0D2B35)" strokeWidth="0.999998" />
            <path d={svgPaths.p20c1be00} id="Vector_2" stroke="var(--stroke-0, #0D2B35)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="0.999999" />
          </g>
        </svg>
      </div>
    </div>
  );
}

function Container40() {
  return (
    <div className="absolute left-[8px] overflow-clip size-[16px] top-[8px]" data-name="Container">
      <G />
    </div>
  );
}

function Container39() {
  return (
    <div className="absolute bg-[#f4f8f8] left-0 rounded-[26843500px] shadow-[0px_1px_2px_0px_rgba(0,0,0,0.1),0px_1px_3px_0px_rgba(0,0,0,0.1)] size-[32px] top-[1.99px]" data-name="Container">
      <Container40 />
    </div>
  );
}

function Container42() {
  return (
    <div className="absolute h-[20px] left-0 top-0 w-[114px]" data-name="Container">
      <p className="absolute font-['Nunito_Sans:Medium',sans-serif] font-medium h-[20px] leading-[20px] left-[-1px] text-[#0d2b35] text-[14px] top-0 w-[97px]" style={{ fontVariationSettings: "'YTLC' 500, 'wdth' 100", fontFeatureSettings: "'dlig'" }}>
        Predicted Peak
      </p>
    </div>
  );
}

function Container43() {
  return (
    <div className="absolute h-[16px] left-0 top-[20px] w-[114px]" data-name="Container">
      <p className="absolute font-['Nunito_Sans:Regular',sans-serif] font-normal h-[16px] leading-[16px] left-[-1px] text-[#637c84] text-[12px] top-0 w-[116px]" style={{ fontVariationSettings: "'YTLC' 500, 'wdth' 100", fontFeatureSettings: "'dlig'" }}>
        Based on latest meal
      </p>
    </div>
  );
}

function Container41() {
  return (
    <div className="absolute h-[36px] left-[44px] top-0 w-[114px]" data-name="Container">
      <Container42 />
      <Container43 />
    </div>
  );
}

function Container38() {
  return (
    <div className="absolute h-[36px] left-[16px] top-[20px] w-[158px]" data-name="Container">
      <Container39 />
      <Container41 />
    </div>
  );
}

function Container46() {
  return (
    <div className="absolute h-[16px] left-[34.71px] top-[8px] w-[37px]" data-name="Container">
      <p className="-translate-x-full absolute font-['Geist:Regular',sans-serif] font-normal h-[16px] leading-[16px] left-[38px] text-[#637c84] text-[12px] text-right top-0 w-[39px]" style={{ fontFeatureSettings: "'dlig'" }}>
        mg/dL
      </p>
    </div>
  );
}

function Container45() {
  return (
    <div className="absolute h-[28px] left-0 top-0 w-[72px]" data-name="Container">
      <p className="-translate-x-full absolute font-['Geist:SemiBold',sans-serif] font-semibold h-[24px] leading-[28px] left-[36px] text-[#0d2b35] text-[18px] text-right top-[1.6px] w-[37px]" style={{ fontFeatureSettings: "'dlig'" }}>
        142
      </p>
      <Container46 />
    </div>
  );
}

function Container48() {
  return (
    <div className="absolute left-[61.61px] size-[12px] top-[1.99px]" data-name="Container">
      <svg className="absolute block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 12 12">
        <g id="Container">
          <path d="M3 9L9 3M9 3H4.5M9 3V7.5" id="Vector" stroke="var(--stroke-0, #F59E0B)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="0.75" />
        </g>
      </svg>
    </div>
  );
}

function Container47() {
  return (
    <div className="absolute h-[16px] left-0 top-[28px] w-[72px]" data-name="Container">
      <p className="-translate-x-full absolute font-['Nunito_Sans:Medium',sans-serif] font-medium h-[16px] leading-[16px] left-[60.01px] text-[#f59e0b] text-[12px] text-right top-[0.2px] w-[60px]" style={{ fontVariationSettings: "'YTLC' 500, 'wdth' 100", fontFeatureSettings: "'dlig'" }}>
        +38 higher
      </p>
      <Container48 />
    </div>
  );
}

function Container44() {
  return (
    <div className="absolute h-[44px] left-[245.19px] top-[16px] w-[72px]" data-name="Container">
      <Container45 />
      <Container47 />
    </div>
  );
}

function Container37() {
  return (
    <div className="absolute bg-[rgba(214,230,225,0.4)] h-[76px] left-[48.8px] rounded-[20px] top-[435.8px] w-[333px]" data-name="Container">
      <Container38 />
      <Container44 />
    </div>
  );
}

function Container52() {
  return (
    <div className="absolute h-[20px] left-0 top-0 w-[109px]" data-name="Container">
      <p className="absolute font-['Nunito_Sans:Medium',sans-serif] font-medium h-[20px] leading-[20px] left-[-1px] text-[#637c84] text-[14px] top-0 w-[187px]" style={{ fontVariationSettings: "'YTLC' 500, 'wdth' 100", fontFeatureSettings: "'dlig'" }}>
        Date Today: March 14, 2026
      </p>
    </div>
  );
}

function Container53() {
  return (
    <div className="absolute h-[28px] left-0 top-[20px] w-[109px]" data-name="Container">
      <p className="absolute font-['Geist:SemiBold',sans-serif] font-semibold h-[24px] leading-[28px] left-[-1px] text-[#0d2b35] text-[18px] top-[2px] tracking-[-0.45px] w-[155px]" style={{ fontFeatureSettings: "'dlig'" }}>
        Hello, User!
      </p>
    </div>
  );
}

function Container51() {
  return (
    <div className="absolute h-[48px] left-[52px] top-0 w-[109px]" data-name="Container">
      <Container52 />
      <Container53 />
    </div>
  );
}

function Container50() {
  return (
    <div className="absolute h-[48px] left-0 top-0 w-[161px]" data-name="Container">
      <div className="absolute bg-size-[230px_230px] bg-top-left left-0 rounded-[26843500px] shadow-[0px_1px_2px_-1px_rgba(0,0,0,0.1),0px_1px_3px_0px_rgba(0,0,0,0.1),0px_0px_0px_2px_rgba(30,97,119,0.1)] size-[40px] top-[4px]" data-name="Image" style={{ backgroundImage: `url('${imgImage}')` }} />
      <Container51 />
    </div>
  );
}

function G1() {
  return (
    <div className="absolute inset-[8.33%_12.5%]" data-name="g">
      <div className="absolute inset-[-3.95%_-7.01%_-3.75%_-7.01%]">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 20.5244 21.5395">
          <g id="g">
            <path d={svgPaths.p1bda9400} id="Vector" stroke="var(--stroke-0, #204A3A)" strokeWidth="1.57896" />
            <path d={svgPaths.p39d0e080} id="Vector_2" stroke="var(--stroke-0, #204A3A)" strokeLinecap="round" strokeWidth="1.5" />
          </g>
        </svg>
      </div>
    </div>
  );
}

function Container54() {
  return (
    <div className="absolute left-[8px] overflow-clip size-[24px] top-[8px]" data-name="Container">
      <G1 />
    </div>
  );
}

function Container55() {
  return <div className="absolute bg-[#d97706] border-[#f4f8f8] border-[1.6px] border-solid right-[10px] rounded-[26843500px] size-[8px] top-[10px]" data-name="Container" />;
}

function Button() {
  return (
    <div className="absolute bg-[rgba(214,230,225,0.5)] left-[342.4px] rounded-[26843500px] size-[40px] top-[4px]" data-name="Button">
      <Container54 />
      <Container55 />
    </div>
  );
}

function Container49() {
  return (
    <div className="absolute h-[48px] left-[24px] top-[16px] w-[383px]" data-name="Container">
      <Container50 />
      <Button />
    </div>
  );
}

function Header() {
  return (
    <div className="absolute backdrop-blur-[12px] bg-[rgba(244,248,248,0.8)] border-[rgba(226,234,235,0.4)] border-b-[0.8px] border-solid h-[81px] left-0 top-0 w-[431px]" data-name="Header">
      <Container49 />
    </div>
  );
}

function Container58() {
  return (
    <div className="absolute h-[17px] left-[8px] top-[38px] w-[32px]" data-name="Container">
      <p className="absolute font-['Geist:SemiBold',sans-serif] font-semibold h-[15px] leading-[16.5px] left-[-1px] text-[#1e6177] text-[11px] top-[0.8px] tracking-[0.275px] w-[34px]" style={{ fontFeatureSettings: "'dlig'" }}>
        Home
      </p>
    </div>
  );
}

function Container60() {
  return (
    <div className="absolute left-0 size-[24px] top-0" data-name="Container">
      <svg className="absolute block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="Container">
          <path clipRule="evenodd" d={svgPaths.p211c7d80} fill="var(--fill-0, #1E6177)" fillRule="evenodd" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function Container61() {
  return <div className="absolute bg-[#1e6177] bottom-[-8px] left-[10px] rounded-[26843500px] size-[4px]" data-name="Container" />;
}

function Container59() {
  return (
    <div className="absolute left-[11.8px] size-[24px] top-[8px]" data-name="Container">
      <Container60 />
      <Container61 />
    </div>
  );
}

function Container57() {
  return (
    <div className="absolute h-[63px] left-[41.45px] top-[8.75px] w-[48px]" data-name="Container">
      <Container58 />
      <Container59 />
    </div>
  );
}

function Container63() {
  return (
    <div className="absolute left-[20.59px] size-[24px] top-[8px]" data-name="Container">
      <svg className="absolute block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="Container">
          <path d={svgPaths.p28858898} id="Vector" stroke="var(--stroke-0, #637C84)" strokeLinecap="round" strokeWidth="1.5" />
        </g>
      </svg>
    </div>
  );
}

function Container64() {
  return (
    <div className="absolute h-[17px] left-[8px] top-[38px] w-[50px]" data-name="Container">
      <p className="absolute font-['Geist:Medium',sans-serif] font-medium h-[15px] leading-[16.5px] left-[-1px] text-[#637c84] text-[11px] top-[0.8px] tracking-[0.275px] w-[52px]" style={{ fontFeatureSettings: "'dlig'" }}>
        Log Meal
      </p>
    </div>
  );
}

function Container62() {
  return (
    <div className="absolute h-[63px] left-[123.96px] top-[8.75px] w-[66px]" data-name="Container">
      <Container63 />
      <Container64 />
    </div>
  );
}

function G2() {
  return (
    <div className="absolute inset-[8.33%]" data-name="g">
      <div className="absolute inset-[-3.75%]">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 21.5 21.5">
          <g id="g">
            <path clipRule="evenodd" d={svgPaths.p1b122900} fillRule="evenodd" id="Vector" stroke="var(--stroke-0, #637C84)" strokeWidth="1.5" />
            <path d={svgPaths.pc126700} id="Vector_2" stroke="var(--stroke-0, #637C84)" strokeLinecap="round" strokeWidth="1.5" />
          </g>
        </svg>
      </div>
    </div>
  );
}

function Container66() {
  return (
    <div className="absolute left-[17.59px] overflow-clip size-[24px] top-[8px]" data-name="Container">
      <G2 />
    </div>
  );
}

function Container67() {
  return (
    <div className="absolute h-[17px] left-[8px] top-[38px] w-[44px]" data-name="Container">
      <p className="absolute font-['Geist:Medium',sans-serif] font-medium h-[15px] leading-[16.5px] left-[-1px] text-[#637c84] text-[11px] top-[0.8px] tracking-[0.275px] w-[46px]" style={{ fontFeatureSettings: "'dlig'" }}>
        Insights
      </p>
    </div>
  );
}

function Container65() {
  return (
    <div className="absolute h-[63px] left-[224.04px] top-[8.75px] w-[60px]" data-name="Container">
      <Container66 />
      <Container67 />
    </div>
  );
}

function G3() {
  return (
    <div className="absolute inset-[8.33%_16.67%]" data-name="g">
      <div className="absolute inset-[-3.75%_-4.69%]">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 17.5003 21.5">
          <g id="g">
            <path clipRule="evenodd" d={svgPaths.p3edfd000} fillRule="evenodd" id="Vector" stroke="var(--stroke-0, #637C84)" strokeWidth="1.5" />
            <path clipRule="evenodd" d={svgPaths.p32979600} fillRule="evenodd" id="Vector_2" stroke="var(--stroke-0, #637C84)" strokeWidth="1.5" />
          </g>
        </svg>
      </div>
    </div>
  );
}

function Container69() {
  return (
    <div className="absolute left-[23.4px] overflow-clip size-[24px] top-[8px]" data-name="Container">
      <G3 />
    </div>
  );
}

function Container70() {
  return (
    <div className="absolute h-[17px] left-[8px] top-[38px] w-[55px]" data-name="Container">
      <p className="absolute font-['Geist:Medium',sans-serif] font-medium h-[15px] leading-[16.5px] left-[-1px] text-[#637c84] text-[11px] top-[0.8px] tracking-[0.275px] w-[57px]" style={{ fontFeatureSettings: "'dlig'" }}>
        My Profile
      </p>
    </div>
  );
}

function Container68() {
  return (
    <div className="absolute h-[63px] left-[318.14px] top-[8.75px] w-[71px]" data-name="Container">
      <Container69 />
      <Container70 />
    </div>
  );
}

function Container56() {
  return (
    <div className="absolute h-[80px] left-0 top-0 w-[431px]" data-name="Container">
      <Container57 />
      <Container62 />
      <Container65 />
      <Container68 />
    </div>
  );
}

function Navigation() {
  return (
    <div className="absolute backdrop-blur-[12px] bg-[rgba(255,255,255,0.9)] border-[rgba(226,234,235,0.5)] border-solid border-t-[0.8px] bottom-0 h-[81px] left-0 w-[430px]" data-name="Navigation">
      <Container56 />
    </div>
  );
}

export default function Home() {
  return (
    <div className="bg-[#f4f8f8] relative size-full" data-name="home 1">
      <Data />
      <AddMeal />
      <NoteNotif />
      <StatusTab />
      <Container20 />
      <Container22 />
      <Container37 />
      <Header />
      <Navigation />
    </div>
  );
}