package view.game.welfare.page
{
   import CommonUI.Button.Button17;
   import CommonUI.Button.Spec.LeftDirButton0;
   import CommonUI.Label.Label;
   import CommonUI.MDPAnimation.MDPMovie;
   import CommonUI.Panel.CustomPanel;
   import CommonUI.Panel.Panel7;
   import CommonUI.Panel.Panel8;
   import CommonUI.Resources.SkinMgr;
   import CommonUI.Scroll.CustomVScrollBar1;
   import CommonUI.baseUI.grid.CustomGrid;
   import CommonUI.baseUI.label.CustomLabel;
   import CommonUI.baseUI.text.TextFactory;
   import common.AchieveDataMgr;
   import common.Data.GameData;
   import common.Data.Items.user.UserItem;
   import common.Data.achieve.std.StdAchieve;
   import common.Data.achieve.user.UserAchieve;
   import common.GameConst;
   import common.GameResource;
   import common.GlobalData;
   import common.globalFunc.GlobalFunc;
   import common.globalFunc.ItemFunc;
   import control.controler.AchieveCC;
   import control.controler.ShopCC;
   import control.navigator.GameNavigateType;
   import control.navigator.GameNavigator;
   import events.AchieveEvent;
   import events.DataEventDispatcher;
   import events.PropertyEvent;
   import flash.display.Bitmap;
   import flash.events.Event;
   import flash.events.MouseEvent;
   import flash.text.TextFieldAutoSize;
   import lang.LangManager;
   import utils.FilterUtils;
   import utils.TextUtils;
   import view.game.components.award.AwardFLCell;
   import view.game.components.progressBar.MDProgressBar1;
   import view.game.firstRecharge.FirstAwardGrid;
   import view.game.welfare.WelfareWin;
   import view.game.welfare.cell.*;

   public class WelFareSurprisePage1 extends WelFareBasePage
   {

      public static var Need_Show_Effect:Boolean = false;


      private var _panel:Panel7;

      private var _achieveConfig:Vector.<StdAchieve>;

      private var _achieveModel:AchieveDataMgr;

      private var _rechargeBtn:Button17;

      private var _getGoldBtn:Button17;

      private var _goldLabel:Bitmap;

      private var _selectedMovie:MDPMovie;

      private var _surpriseGrid:CustomGrid;

      private var _vScrollBar:CustomVScrollBar1;

      private var _currentSelectedCell:RechargeSurpriseItem2Cell;

      private var _giftCellBg:Panel7;

      private var _grid:FirstAwardGrid;

      private var _nonecAchieve:StdAchieve;

      private var _getGiftBtn:Button17;

      private var _nonceDistillAmount:Label;

      private var _discrepancyAmount:Label;

      private var _getYanBaoTxt:CustomLabel;

      private var _haichaTxt:CustomLabel;

      private var _dalibaoTxt:CustomLabel;

      private var _nextStd:StdAchieve;

      private var _nextStdMessage:StdAchieve;

      private var _tangetScrollBar:CustomVScrollBar1;

      private var _progressBar:MDProgressBar1;

      private var _proLabel:Label;

      private var _libaoLabel:Label;

      private var nowPage:int = 1;

      private var everyPageNum:int = 12;

      private var maxPage:int = 0;

      private var _leftBtn:LeftDirButton0;

      private var _rightBtn:LeftDirButton0;

      public function WelFareSurprisePage1()
      {
         var bg3:Panel8 = null;
         var bg1:Panel7 = null;
         var bg2:Panel7 = null;
         var surpiseTxt:Bitmap = null;
         var useritem:UserItem = null;
         super();
         var bg:CustomPanel = new CustomPanel();
         bg.setSize(720,465);
         this.addChild(bg);
         this.move(-12,0);
         var gridBg:CustomPanel = new CustomPanel();
         gridBg.setSize(bg.uiWidth,380);
         bg.addChild(gridBg);
         this._giftCellBg = new Panel7(SkinMgr.WinBg1);
         this._giftCellBg.setSize(gridBg.uiWidth,380);
         this._giftCellBg.move(0,0);
         gridBg.addChild(this._giftCellBg);
         var vLabel:Label = new Label();
         vLabel.setSize(gridBg.uiWidth,30);
         vLabel.autoSize = TextFieldAutoSize.CENTER;
         TextUtils.labSetCaption(vLabel,LangManager.Lang.welfare[68],[15785216,15693824],16724787,18,"黑体");
         vLabel.move(0,15);
         this._giftCellBg.addChild(vLabel);
         bg3 = new Panel8(SkinMgr.WinBg1);
         bg3.setSize(gridBg.uiWidth,80);
         bg3.move(gridBg.x,gridBg.y + gridBg.uiHeight + 5);
         bg.addChild(bg3);
         this._proLabel = new Label();
         this._proLabel.move(40,15);
         TextUtils.labSetCaption(this._proLabel,LangManager.Lang.welfare[67].toString().replace("$value$",0),[15785216,15693824],16724787,18,"黑体");
         bg3.addChild(this._proLabel);
         this._progressBar = new MDProgressBar1(MDProgressBar1.ORANGE);
         this._progressBar.width = 380;
         this._progressBar.max = 1;
         this._progressBar.move(25,35);
         this._progressBar.formatTextFn = this.formatTxtFunc;
         this._progressBar.setProgress(0,1);
         bg3.addChild(this._progressBar);
         bg1 = new Panel7(SkinMgr.WinBg1);
         bg1.setSize((gridBg.uiWidth >> 1) - 5,bg.uiHeight - gridBg.x - gridBg.uiHeight - 10);
         bg1.move(gridBg.x,gridBg.y + gridBg.uiHeight + 5);
         bg2 = new Panel7(SkinMgr.WinBg1);
         bg2.setSize(bg1.width,bg1.uiHeight);
         bg2.move(bg1.x + bg1.uiWidth + 10,bg1.y);
         surpiseTxt = new Bitmap(TextFactory.createText(LangManager.Lang.welfare[11],16777215,false,FilterUtils.DefaultTextFilters));
         surpiseTxt.x = 35;
         surpiseTxt.y = 15;
         bg1.addChild(surpiseTxt);
         var surpiseTxtI:Bitmap = new Bitmap(TextFactory.createText(LangManager.Lang.welfare[50],16777215,false,FilterUtils.DefaultTextFilters));
         surpiseTxtI.x = 30;
         surpiseTxtI.y = 60;
         bg1.addChild(surpiseTxtI);
         this._goldLabel = new Bitmap();
         this._goldLabel.x = surpiseTxt.x;
         this._goldLabel.y = 10;
         bg2.addChild(this._goldLabel);
         this._getGoldBtn = new Button17();
         this._getGoldBtn.caption = LangManager.Lang.Common_GetGole;
         this._getGoldBtn.move(bg3.uiWidth - this._getGoldBtn.uiWidth - 20,bg3.uiHeight - this._getGoldBtn.uiHeight - 5);
         this._rechargeBtn = new Button17();
         this._rechargeBtn.autoSize = false;
         this._rechargeBtn.setSize(120,57);
         this._rechargeBtn.caption = "<font size = \'16\'><b>" + LangManager.Lang.welfare[12] + "</b></font>";
         this._rechargeBtn.move(bg3.width - 30 - this._rechargeBtn.width - 280,12);
         bg3.addChild(this._rechargeBtn);
         this._getGiftBtn = new Button17();
         this._getGiftBtn.autoSize = false;
         this._getGiftBtn.setSize(120,57);
         this._getGiftBtn.move(this._rechargeBtn.x - 20 - this._getGiftBtn.width,this._rechargeBtn.y);
         bg3.addChild(this._getGiftBtn);
         this._getGiftBtn.caption = "<font size = \'16\'><b>" + LangManager.Lang.landingReward[1] + "</b></font>";
         this._achieveConfig = GameData.achieveProvider.awardAchieveList;
         this._achieveModel = GlobalData.achieveDataMgr;
         this._surpriseGrid = new CustomGrid(RechargeSurpriseItem2Cell);
         var _loc2_:*;
         with(_loc2_ = this._surpriseGrid)
         {

            cellWidth = RechargeSurpriseItem2Cell.WIDTH;
            cellHeight = RechargeSurpriseItem2Cell.HEIGHT + 10;
            colCount = 6;
            gridSpaceWidth = 40;
            gridSpaceHeight = 50;
            mouseEnabled = true;
            enableDragCell = false;
            setSize(cellWidth * colCount + gridSpaceWidth * (colCount - 1),cellHeight * 3 + gridSpaceHeight * (2 - 1));
         }
         this._surpriseGrid.move(this._giftCellBg.uiWidth - this._surpriseGrid.uiWidth >> 1,40);
         this._giftCellBg.addChild(this._surpriseGrid);
         this._surpriseGrid.rowCount = 4;
         this._leftBtn = new LeftDirButton0();
         this._leftBtn.move(15,155);
         this.addChild(this._leftBtn);
         this._rightBtn = new LeftDirButton0();
         this._rightBtn.rotation = 180;
         this._rightBtn.move(705,200);
         this.addChild(this._rightBtn);
         this.nowPage = 1;
         this._leftBtn.visible = false;
         this.maxPage = (this._achieveConfig.length - 4) / this.everyPageNum;
         if(int((this._achieveConfig.length - 4) % this.everyPageNum) > 0)
         {
            this.maxPage = this.maxPage + 1;
         }
         if(this.maxPage > 1)
         {
            this._rightBtn.visible = true;
         }
         else
         {
            this._rightBtn.visible = false;
         }
         this._libaoLabel = new Label();
         var userAchieve:UserAchieve = null;
         if(this._achieveConfig.length)
         {
            userAchieve = this._achieveModel.getUserAchieveAt((this._achieveConfig[0] as StdAchieve).id);
         }
         if(userAchieve != null)
         {
            if(userAchieve.stdAchieve.awards[0])
            {
               useritem = ItemFunc.makeUserItemFromAward(userAchieve.stdAchieve.awards[0]);
            }
            else
            {
               useritem = ItemFunc.makeUserItemFromAward(userAchieve.stdAchieve.gift[0]);
            }
            TextUtils.labSetCaption(this._libaoLabel,useritem.stdItem.name,[15785216,15693824],16724787,18,"黑体");
         }
         this._libaoLabel.move(30,this._surpriseGrid.y + this._surpriseGrid.height + 42);
         this._giftCellBg.addChild(this._libaoLabel);
         this._grid = new FirstAwardGrid(AwardFLCell);
         with(_loc2_ = this._grid)
         {

            cellWidth = cellHeight = 40;
            gridSpaceWidth = 13;
            gridSpaceHeight = 20;
            colCount = 9;
            rowCount = 1;
            setSize(cellWidth * colCount + gridSpaceWidth * (colCount - 1),cellHeight * rowCount + gridSpaceHeight * (rowCount - 1));
         }
         this._grid.move(this._libaoLabel.x + this._libaoLabel.width + 25,this._libaoLabel.y - 15);
         this._giftCellBg.addChild(this._grid);
         this._selectedMovie = new MDPMovie(GameResource.defaultResource.getEffect(10));
         this._selectedMovie.scaleX = 76 / 35;
         this._selectedMovie.scaleY = 0.8;
         this._selectedMovie.move(bg2.x + 24,bg2.y + 83);
         addChild(this._selectedMovie);
         this._nonecAchieve = null;
         this._getYanBaoTxt = new CustomLabel();
         this._getYanBaoTxt.useGradientText = true;
         this._getYanBaoTxt.GradientTextBold = true;
         this._getYanBaoTxt.GradientTextColors = [16763904,16711680];
         this._getYanBaoTxt.textFilters = FilterUtils.DefaultTextFilters;
         this._getYanBaoTxt.caption = LangManager.Lang.other[7];
         bg2.addChild(this._getYanBaoTxt);
         this._getYanBaoTxt.move(30,10);
         this._nonceDistillAmount = new Label();
         this._nonceDistillAmount.move(this._getYanBaoTxt.width + 30,10);
         bg2.addChild(this._nonceDistillAmount);
         this._haichaTxt = new CustomLabel();
         this._haichaTxt.move(60,40);
         this._haichaTxt.useGradientText = true;
         this._haichaTxt.GradientTextBold = true;
         this._haichaTxt.GradientTextColors = [16763904,16711680];
         this._haichaTxt.textFilters = FilterUtils.DefaultTextFilters;
         this._haichaTxt.caption = LangManager.Lang.other[8];
         bg2.addChild(this._haichaTxt);
         this._discrepancyAmount = new Label();
         bg2.addChild(this._discrepancyAmount);
         this._discrepancyAmount.move(this._haichaTxt.x + this._haichaTxt.width + 5,this._haichaTxt.y);
         this._dalibaoTxt = new CustomLabel();
         this._dalibaoTxt.move(165,40);
         this._dalibaoTxt.useGradientText = true;
         this._dalibaoTxt.GradientTextBold = true;
         this._dalibaoTxt.GradientTextColors = [16763904,16711680];
         this._dalibaoTxt.textFilters = FilterUtils.DefaultTextFilters;
         this._dalibaoTxt.caption = LangManager.Lang.other[9];
         bg2.addChild(this._dalibaoTxt);
      }

      private function setInfo(param1:Number, param2:Number, param3:Number, param4:int, param5:StdAchieve = null) : void
      {
         var _loc6_:StdAchieve = null;
         var _loc7_:UserAchieve = null;
         var _loc8_:UserAchieve = null;
         var _loc9_:UserItem = null;
         var _loc10_:UserItem = null;
         var _loc12_:String = null;
         if(!this._achieveConfig.length)
         {
            return;
         }
         if(param5 == null)
         {
            _loc6_ = this._achieveConfig[param4] as StdAchieve;
         }
         else
         {
            _loc6_ = param5;
         }
         if(this._nextStdMessage)
         {
            _loc8_ = this._achieveModel.getUserAchieveAt(this._nextStdMessage.id);
         }
         else
         {
            _loc8_ = null;
         }
         if((_loc7_ = this._achieveModel.getUserAchieveAt(_loc6_.id)).stdAchieve.awards[0])
         {
            _loc9_ = ItemFunc.makeUserItemFromAward(_loc7_.stdAchieve.awards[0]);
            if(_loc8_)
            {
               _loc10_ = ItemFunc.makeUserItemFromAward(_loc8_.stdAchieve.awards[0]);
            }
         }
         else
         {
            _loc9_ = ItemFunc.makeUserItemFromAward(_loc7_.stdAchieve.gift[0]);
            if(_loc8_)
            {
               _loc10_ = ItemFunc.makeUserItemFromAward(_loc8_.stdAchieve.awards[0]);
            }
         }
         this._progressBar.max = param3;
         this._progressBar.setProgress(param2,param3);
         _loc12_ = param1 >= 1000000000?(Math.round(param1 / 100000000) / 10).toString().replace(".0","") + "B":param1 >= 1000000?(Math.round(param1 / 100000) / 10).toString().replace(".0","") + "M":param1 >= 1000?(Math.round(param1 / 100) / 10).toString().replace(".0","") + "K":param1.toString();
         var _loc11_:String = LangManager.Lang.welfare[67].toString().replace("$value$",_loc12_);
         if(_loc10_)
         {
            _loc11_ = _loc11_.replace("$libao$",_loc10_.stdItem.name);
            TextUtils.labSetCaption(this._proLabel,_loc11_,[15785216,15693824],16724787,18,"黑体");
         }
         else
         {
            _loc11_ = _loc11_.replace("$libao$",_loc9_.stdItem.name);
            TextUtils.labSetCaption(this._proLabel,_loc11_,[15785216,15693824],16724787,18,"黑体");
         }
      }

      public function playEffect() : void
      {
         this._selectedMovie.visible = true;
         this._selectedMovie.play();
         Need_Show_Effect = false;
      }

      override public function initEvent() : void
      {
         this._rechargeBtn.addEventListener(MouseEvent.CLICK,this.onFunClickHandler);
         this._getGoldBtn.addEventListener(MouseEvent.CLICK,this.onFunClickHandler);
         this._surpriseGrid.addEventListener(MouseEvent.CLICK,this.onCellSelected);
         DataEventDispatcher.addEventListener(AchieveEvent.ACHIEVE_AWARDS_GOT,this.onAchieveProgress);
         DataEventDispatcher.addEventListener(AchieveEvent.ACHIEVE_INIT,this.onAchieveProgress);
         DataEventDispatcher.addEventListener(AchieveEvent.ACHIEVE_FINISHED,this.onAchieveProgress);
         DataEventDispatcher.addEventListener(PropertyEvent.MAIN_MONEY_CHANGE,this.onPropertyChange);
         this._getGiftBtn.addEventListener(MouseEvent.CLICK,this.onFunClickHandler);
         this._leftBtn.addEventListener(MouseEvent.CLICK,this.truneLeftByBtn);
         this._rightBtn.addEventListener(MouseEvent.CLICK,this.truneRightByBtn);
         if(Need_Show_Effect)
         {
            this.playEffect();
         }
         this.setAchieveData();
         this.setNonecPhaseData();
         this.onPropertyChange(null);
      }

      override public function removeEvent() : void
      {
         this._rechargeBtn.removeEventListener(MouseEvent.CLICK,this.onFunClickHandler);
         this._getGoldBtn.removeEventListener(MouseEvent.CLICK,this.onFunClickHandler);
         DataEventDispatcher.removeEventListener(AchieveEvent.ACHIEVE_AWARDS_GOT,this.onAchieveProgress);
         DataEventDispatcher.removeEventListener(AchieveEvent.ACHIEVE_INIT,this.onAchieveProgress);
         DataEventDispatcher.removeEventListener(AchieveEvent.ACHIEVE_FINISHED,this.onAchieveProgress);
         DataEventDispatcher.removeEventListener(PropertyEvent.MAIN_MONEY_CHANGE,this.onPropertyChange);
         this._surpriseGrid.removeEventListener(MouseEvent.CLICK,this.onCellSelected);
         this._getGiftBtn.removeEventListener(MouseEvent.CLICK,this.onFunClickHandler);
         this._leftBtn.removeEventListener(MouseEvent.CLICK,this.truneLeftByBtn);
         this._rightBtn.removeEventListener(MouseEvent.CLICK,this.truneRightByBtn);
         this._selectedMovie.visible = false;
         this._selectedMovie.stop();
         if(this._currentSelectedCell)
         {
            this._currentSelectedCell.filters = null;
            this._currentSelectedCell.selected = false;
            this._currentSelectedCell = null;
         }
      }

      private function setNonecPhaseData() : void
      {
         var _loc5_:StdAchieve = null;
         var _loc6_:UserAchieve = null;
         var _loc7_:int = 0;
         var _loc8_:RechargeSurpriseItem2Cell = null;
         var _loc9_:UserItem = null;
         if(!GlobalData.achieveDataMgr.hasInit())
         {
            return;
         }
         var _loc1_:Boolean = true;
         var _loc2_:int = 0;
         this._grid.clear();
         var _loc3_:int = this._achieveConfig.length;
         var _loc4_:int = 0;
         while(_loc4_ < _loc3_)
         {
            if(_loc5_ = this._achieveConfig[_loc4_])
            {
               if(!(_loc5_.id == GameConst.FIRST_RECHARGE_AWARD || _loc5_.id == GameConst.FIRST_RECHARGE_TWO_AWARD || _loc5_.id == GameConst.FIRST_RECHARGE_THREE_AWARD || _loc5_.id == GameConst.FIRST_RECHARGE_FOUR_AWARD))
               {
                  if(!(!(_loc6_ = this._achieveModel.getUserAchieveAt(_loc5_.id)) || !_loc6_.stdAchieve))
                  {
                     if(_loc6_.hasDone && _loc6_.hasGetAwards && _loc1_)
                     {
                        this._nonecAchieve = _loc5_;
                        _loc2_ = _loc4_;
                     }
                     if(!_loc6_.hasDone && !_loc6_.hasGetAwards && _loc1_)
                     {
                        this._nonecAchieve = _loc5_;
                        _loc1_ = false;
                        _loc2_ = _loc4_;
                     }
                     if(_loc6_.hasDone && !_loc6_.hasGetAwards)
                     {
                        this._nonecAchieve = _loc5_;
                        _loc2_ = _loc4_;
                        break;
                     }
                  }
               }
            }
            _loc4_++;
         }
         if(this._nonecAchieve)
         {
            _loc7_ = 0;
            while(_loc7_ < this._surpriseGrid.numChildren)
            {
               if((_loc8_ = this._surpriseGrid.getByIndex(_loc7_) as RechargeSurpriseItem2Cell).data && (_loc8_.data as UserAchieve).stdAchieve == this._nonecAchieve)
               {
                  if(this._currentSelectedCell)
                  {
                     this._currentSelectedCell.selected = false;
                  }
                  this._currentSelectedCell = _loc8_;
                  this._currentSelectedCell.selected = true;
                  this.setCellData(this._nonecAchieve);
                  _loc9_ = ItemFunc.makeUserItemFromAward(this._nonecAchieve.awards[0]);
                  TextUtils.labSetCaption(this._libaoLabel,_loc9_.stdItem.name,[15785216,15693824],16724787,18,"黑体");
                  break;
               }
               _loc7_++;
            }
         }
         this.nextNoAchieve();
      }

      private function nextNoAchieve() : void
      {
         var _loc3_:StdAchieve = null;
         var _loc4_:UserAchieve = null;
         if(!GlobalData.achieveDataMgr.hasInit())
         {
            return;
         }
         var _loc1_:int = this._achieveConfig.length;
         var _loc2_:int = 0;
         while(_loc2_ < _loc1_)
         {
            _loc3_ = this._achieveConfig[_loc2_];
            if(!(_loc3_.id == GameConst.FIRST_RECHARGE_AWARD || _loc3_.id == GameConst.FIRST_RECHARGE_TWO_AWARD || _loc3_.id == GameConst.FIRST_RECHARGE_THREE_AWARD || _loc3_.id == GameConst.FIRST_RECHARGE_FOUR_AWARD))
            {
               if(!(_loc4_ = this._achieveModel.getUserAchieveAt(_loc3_.id)).stdAchieve.isDelete)
               {
                  if(!_loc4_.hasDone && !_loc4_.hasGetAwards)
                  {
                     if(_loc3_.id == GameConst.FIRST_AWARD_GIFE)
                     {
                        this._discrepancyAmount.caption = LangManager.Lang.welfare[49].toString().replace("$money$",_loc3_.nowAim);
                        this.setInfo(_loc3_.nowAim,GlobalData.role.drawYBCount,_loc3_.nowAim,0);
                     }
                     else if(_loc2_ != 0)
                     {
                        this._nextStd = this._achieveConfig[_loc2_ - 1];
                        this._nextStdMessage = this._achieveConfig[_loc2_];
                     }
                     return;
                  }
               }
            }
            _loc2_++;
         }
         this._discrepancyAmount.caption = LangManager.Lang.welfare[49].toString().replace("$money$",0);
         TextUtils.labSetCaption(this._proLabel,LangManager.Lang.welfare[67].toString().replace("$value$",0),[15785216,15693824],16724787,18,"黑体");
         this.setInfo(0,0,0,0);
      }

      private function setCellData(param1:StdAchieve) : void
      {
         var _loc2_:Boolean = false;
         this._grid.clear();
         var _loc3_:int = param1.gift.length;
         var _loc4_:int = 0;
         while(_loc4_ < _loc3_)
         {
            if(param1.gift[_loc4_].job && param1.gift[_loc4_].sex != -1)
            {
               if(param1.gift[_loc4_].job == GlobalData.role.job && param1.gift[_loc4_].sex - 1 == GlobalData.role.sex)
               {
                  this._grid.addData(param1.gift[_loc4_]);
               }
            }
            else if(param1.gift[_loc4_].job)
            {
               if(param1.gift[_loc4_].job == GlobalData.role.job)
               {
                  this._grid.addData(param1.gift[_loc4_]);
               }
            }
            else if(param1.gift[_loc4_].sex != -1)
            {
               if(param1.gift[_loc4_].sex - 1 == GlobalData.role.sex)
               {
                  this._grid.addData(param1.gift[_loc4_]);
               }
            }
            else
            {
               this._grid.addData(param1.gift[_loc4_]);
            }
            _loc4_++;
         }
      }

      private function onCellSelected(param1:MouseEvent) : void
      {
         var _loc3_:UserAchieve = null;
         var _loc4_:UserItem = null;
         var _loc5_:UserAchieve = null;
         var _loc2_:RechargeSurpriseItem2Cell = this._surpriseGrid.getCellAtXY(this._surpriseGrid.mouseX,this._surpriseGrid.mouseY) as RechargeSurpriseItem2Cell;
         if(_loc2_ && _loc2_.data)
         {
            if(_loc2_ == this._currentSelectedCell)
            {
               return;
            }
            if(this._currentSelectedCell)
            {
               this._currentSelectedCell.selected = false;
            }
            this._currentSelectedCell = _loc2_;
            if(this._currentSelectedCell.boxImgVisble)
            {
               this._currentSelectedCell.selected = true;
            }
            _loc3_ = this._achieveModel.getUserAchieveAt((_loc2_.data as UserAchieve).stdAchieve.id);
            if(_loc3_.stdAchieve.awards[0])
            {
               _loc4_ = ItemFunc.makeUserItemFromAward(_loc3_.stdAchieve.awards[0]);
            }
            else
            {
               _loc4_ = ItemFunc.makeUserItemFromAward(_loc3_.stdAchieve.gift[0]);
            }
            TextUtils.labSetCaption(this._libaoLabel,_loc4_.stdItem.name,[15785216,15693824],16724787,18,"黑体");
            this.setCellData((_loc2_.data as UserAchieve).stdAchieve);
            _loc5_ = this._achieveModel.getUserAchieveAt(this._nonecAchieve.id);
            this._nonecAchieve = (_loc2_.data as UserAchieve).stdAchieve;
            if(!_loc5_.hasDone || _loc5_.hasGetAwards)
            {
            }
         }
      }

      private function onAchieveProgress(param1:AchieveEvent) : void
      {
         this.setNonecPhaseData();
         this.setAchieveData();
         this.nextNoAchieve();
      }

      private function onAchieveHandler(param1:AchieveEvent) : void
      {
         this.setNonecPhaseData();
      }

      private function setAchieveData() : void
      {
         var _loc1_:UserAchieve = null;
         var _loc2_:StdAchieve = null;
         if(!GlobalData.achieveDataMgr.hasInit())
         {
            return;
         }
         this._surpriseGrid.clear();
         var _loc3_:int = (this.nowPage - 1) * this.everyPageNum;
         var _loc4_:int;
         if((_loc4_ = this.nowPage * this.everyPageNum) > this._achieveConfig.length)
         {
            _loc4_ = this._achieveConfig.length;
         }
         while(_loc3_ < _loc4_)
         {
            _loc2_ = this._achieveConfig[_loc3_] as StdAchieve;
            if(!(_loc2_.id == GameConst.FIRST_RECHARGE_AWARD || _loc2_.id == GameConst.FIRST_RECHARGE_TWO_AWARD || _loc2_.id == GameConst.FIRST_RECHARGE_THREE_AWARD || _loc2_.id == GameConst.FIRST_RECHARGE_FOUR_AWARD))
            {
               _loc1_ = this._achieveModel.getUserAchieveAt(_loc2_.id);
               if(_loc1_)
               {
                  this._surpriseGrid.addData(_loc1_);
               }
            }
            _loc3_++;
         }
      }

      private function onFunClickHandler(param1:MouseEvent) : void
      {
         switch(param1.currentTarget)
         {
            case this._getGoldBtn:
               ShopCC.sendQueryMyYuanBao();
               break;
            case this._rechargeBtn:
               GlobalFunc.recharge();
               this._selectedMovie.stop();
               this._selectedMovie.visible = false;
               break;
            case this._getGiftBtn:
               if(this._nonecAchieve != null)
               {
                  AchieveCC.sendGetAwards(this._nonecAchieve.id);
               }
         }
      }

      private function onPropertyChange(param1:PropertyEvent) : void
      {
         this._nonceDistillAmount.caption = LangManager.Lang.welfare[49].toString().replace("$money$",GlobalData.role.drawYBCount);
         if(this._nextStd)
         {
            this.discrepancy(this._nextStd);
         }
         if(param1 != null)
         {
            this.setNonecPhaseData();
         }
      }

      private function discrepancy(param1:StdAchieve) : void
      {
         var _loc3_:String = null;
         if(!param1)
         {
            this._discrepancyAmount.caption = LangManager.Lang.welfare[49].toString().replace("$money$",0);
            this._progressBar.max = 1;
            this._progressBar.setProgress(0,1);
            this.setInfo(0,0,1,0);
            return;
         }
         var _loc2_:int = param1.nextAim - GlobalData.role.drawYBCount;
         if(_loc2_ <= 0)
         {
            _loc2_ = 0;
         }
         _loc3_ = _loc2_ >= 1000000000?(Math.round(_loc2_ / 100000000) / 10).toString().replace(".0","") + "B":_loc2_ >= 1000000?(Math.round(_loc2_ / 100000) / 10).toString().replace(".0","") + "M":_loc2_ >= 1000?(Math.round(_loc2_ / 100) / 10).toString().replace(".0","") + "K":_loc2_.toString();
         this._discrepancyAmount.caption = LangManager.Lang.welfare[49].toString().replace("$money$",_loc3_);
         this._progressBar.max = param1.nextAim;
         this._progressBar.setProgress(GlobalData.role.drawYBCount,param1.nextAim);
         this.setInfo(_loc2_,GlobalData.role.drawYBCount,param1.nextAim,param1.id,param1);
      }

      private function onSelectCell(param1:Event) : void
      {
      }

      override public function set visible(param1:Boolean) : void
      {
         super.visible = param1;
         if(param1)
         {
            if(GameNavigator.getWinByType(GameNavigateType.WIN_WelFare) as WelfareWin != null)
            {
               (GameNavigator.getWinByType(GameNavigateType.WIN_WelFare) as WelfareWin).setWinSize(2);
            }
         }
      }

      private function truneLeftByBtn(param1:MouseEvent) : void
      {
         if(this.nowPage != 1)
         {
            this.nowPage = this.nowPage - 1;
            this.setAchieveData();
            this._rightBtn.visible = true;
            if(this.nowPage == 1)
            {
               this._leftBtn.visible = false;
            }
         }
      }

      private function truneRightByBtn(param1:MouseEvent) : void
      {
         if(this.nowPage != this.maxPage)
         {
            this.nowPage = this.nowPage + 1;
            this.setAchieveData();
            this._leftBtn.visible = true;
            if(this.nowPage == this.maxPage)
            {
               this._rightBtn.visible = false;
            }
         }
      }

      private function formatTxtFunc(param1:Number, param2:Number) : String
      {
         var _loc3_:String = param1 >= 1000000000?(Math.round(param1 / 100000000) / 10).toString().replace(".0","") + "B":param1 >= 1000000?(Math.round(param1 / 100000) / 10).toString().replace(".0","") + "M":param1 >= 1000?(Math.round(param1 / 100) / 10).toString().replace(".0","") + "K":param1.toString();
         var _loc4_:String = param2 >= 1000000000?(Math.round(param2 / 100000000) / 10).toString().replace(".0","") + "B":param2 >= 1000000?(Math.round(param2 / 100000) / 10).toString().replace(".0","") + "M":param2 >= 1000?(Math.round(param2 / 100) / 10).toString().replace(".0","") + "K":param2.toString();
         return _loc3_ + "/" + _loc4_;
      }
   }
}
